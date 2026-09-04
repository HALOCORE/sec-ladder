\section{Method, and one thing it is not}
\label{sec:method}

%%literal-ok 108  p06's instruction span, not the trusted-item count
%% Apparatus only.  The adversarial protocol, the outcome-matrix caveat and the
%% positive-control rule live in \ref{sec:hostile}, beside the figures they
%% qualify.  Every figure here is a \num{} live from data/index.json or carries
%% a \src{} chip.
%% ⚠ \figure{}{} MUST BE ON ONE LINE — paper.js matches it with a single-line
%% regex and silently drops a wrapped one, taking its \label with it.

This section is apparatus: what a cell is, what the primary metric does and does
not measure, and the one rule that keeps a proof from being vacuous. None of it
is a finding, so a reader who wants results now should skip to \ref{sec:hostile}
and come back when a number starts to look too clean to believe.

\subsection{What a cell is}

The unit of measurement is a **cell**: one pattern, at one rung, built at one
optimisation level, in one inlining mode. A *pattern* is a small C kernel that
does one recognisable job — a TLV walker, a bounded stack, a `strncpy`
truncation — and carries one bug class inside it. A *rung* is one of the six
ways to write that kernel, from plain, unchecked C with the bug (**R1**) to
unsafe Rust whose obligations Verus discharges (**R5**). R1 and hardened C
(**R1h**) are each built by gcc and by clang; the optimisation levels are `-O0`
and `-O3`; the inlining modes are `isolated`, where the kernel keeps its own
symbol, and `whole`, where it may be inlined into `main`. That is 32 cells for a
pattern with the full rung set, and \num{totals.cells} across
\num{totals.patterns} patterns drawn from a \num{totals.catalogue}-row
catalogue.

Two things hold the comparison together, and both are enforced rather than
asserted.

**The driver is pinned, not assumed identical.** The kernel is the pattern; the
driver is boilerplate — read the file, loop, fold, print. It cannot be
byte-identical across two languages, so `harness/dloop.py` normalises the C and
the Rust driver loops to one language-neutral token sequence, and the pattern's
`spec.md` pins that sequence with a hash taken before any cell is built
\src{results/gate/*.json}. This is not ceremony: a seven-substring check on p01's
C driver once passed with a `__builtin_prefetch` and an `__asm__ __volatile__`
memory barrier added to the measured loop \src{.memory/02-bench-rules.md}.

**Correctness is decided by a third party.** It is not "the rungs agree with
each other". Each pattern ships `model.py`, an independent Python reference
implementation, and every rung's exit code and stdout is compared against
that.

\begin{caveat}{A green Miri row is one draw}
Miri decides the aliasing questions here, and it runs at its default
configuration: **Stacked Borrows**, and **no seed** — the gate sets no
`MIRIFLAGS` and every one of the \num{totals.patterns} gate records carries a
null flag string \src{results/gate/*.json}. Tree Borrows is never run anywhere in
the shipped matrix. What is left unpinned is a draw. The same source has
returned a clean verdict in one launch environment and an undefined-behaviour
verdict in another, and this project has now been wrong **twice** about which
knob selects which: *seed versus seed*, refuted by identical verdicts over seeds
0…11, and then *`MIRIFLAGS` present versus absent*, refuted when the `miri`
driver turned out never to read that variable. What is measured is that a decoy
environment variable with nothing to do with Miri flips the verdict exactly as
`-Zmiri-seed=0` does, and that the address draw is deterministic at a fixed
environment and moves with it \src{.memory/00-environment.md}. So
`miri_version` pins the interpreter and nothing pins the draw — not even the
gate record, which reads the same either way. Read this paper's
\num{totals.miri_ub|plain} undefined-behaviour findings in
\num{totals.miri_runs} Miri runs as *no undefined behaviour on the draw that
ran*, never as *no undefined behaviour*.
\end{caveat}

\subsection{Why executed instructions, and not wall clock}

The primary metric is `Ir` — instructions executed, counted by valgrind's
callgrind, reported per kernel call. It is deterministic and reproducible to the
instruction. Wall clock on this box is not, and that is a measured result rather
than an excuse.

\figure{spread}{The layout control. One pattern's Rust rungs, built many ways from identical source: same instruction count, same normalised machine code, only the address of the kernel moves. Each row is one rung-to-rung comparison, the band its range over the build population, the centre line zero.}
\label{fig:spread}

The control in \ref{fig:spread} builds \pat{p01}'s rungs
\num{layout.rungs.unsafe.builds} ways each, moving the kernel to
\num{layout.rungs.unsafe.addresses} distinct addresses at an unchanged
instruction stream and an unchanged normalised function digest. All
\num{layout.flips} rung-to-rung comparisons in the control **change sign** across
that population, and elsewhere in the tree the effect reaches 27% of wall clock
\src{.memory/03-measurement.md}. Its reach is uneven, which matters more than the
headline: the geometry flips on every pattern examined, but the *time* moves only
on front-end-bound loops — sign-flipping on p07 and \pat{p01}, absent on p02,
p05, p16 and p17. A single-layout comparison cannot tell you which case you are
in, so this paper quotes no cross-pattern wall-clock column at all.
\ref{sec:lies} is the retraction underneath that decision.

Two conventions of `Ir` exist and they are not interchangeable.
*Kernel-exclusive* counts instructions inside the kernel symbol only.
*Whole-program marginal* is a difference of two run lengths and therefore
includes the callees. They disagree whenever the rungs dispatch different work
outside the kernel symbol — at `-O0` on p08, one respelling of the same load
reads `+2` per call in the first convention and `+27` in the second, because the
work moved into a callee \src{.memory/03-measurement.md}. The generated tables
are uniformly kernel-exclusive; a pattern's own notes may quote either, and the
standing rule is that every figure names its convention.

And `Ir` is not time in the other direction either. On p06 under clang the
hardened rung executes 45–108 *fewer* instructions and runs 10–20% slower
\src{results/SYNTHESIS.md}.

\subsection{The precondition rule}

This is the rule that makes the proofs mean anything, and it is easy to get
wrong in a way that verifies.

\begin{principle}{The precondition is structural; the attack is data}
A kernel's `requires` may state only structural facts — the slices exist, the
offsets are in range, the buffer capacities are what they are. It may never be
about the *contents* of the buffer the driver built. Every attacker-controlled
quantity is an **argument**, not an assumption: a length prefix read from the
payload is data, and the kernel must be total in all 65 536 values a `u16` can
take. The security property lives in the `ensures`. A `requires` that excludes
the attack has not solved the problem, it has assumed it away — and it will
verify, and a naive gate will pass it \src{.memory/02-bench-rules.md}.
\end{principle}

The gate enforces this rather than trusting it: it reads the kernel's `requires`
and `ensures` out of `spec.md` and evaluates the precondition at every call the
benchmark actually makes. Across the corpus the precondition held on all
\num{totals.plain_c.rows} adversarial inputs, over 617 496 kernel calls, of which
36 inputs make zero calls — the driver rejects the file first — leaving 93 that
exercise the contract under attack \src{results/gate/*.json}. Separately, every
R5 kernel must have a call site that is itself verified: if the kernel is
reachable only from an `external_body` `main`, no precondition is ever
discharged and the proof constrains nothing.

A cell fixes what is being compared, a convention fixes what the count contains,
and a precondition fixes who must establish the fact the kernel relies on. So the
numbers that follow are not a price list but a record of where each rung put the
obligation, and of who is left holding it.
