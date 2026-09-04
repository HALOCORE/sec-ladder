\section{What unchecked C actually does}
\label{sec:hostile}

%% The practitioner's section.  Headline is re-derived from results/gate/*.json
%% rather than quoted; the denominator and the aggregation rule are both stated
%% because the split moves when the rule moves.
%% RECEIVED FROM \ref{sec:method}: the adversarial protocol, the outcome-matrix
%% caveat, and the positive-control rule (now the principle opening "What the
%% detectors saw").  This section is the ONE HOME for the `__memcpy_chk` /
%% `_FORTIFY_SOURCE` blindness -- elsewhere it is a clause and a \ref.
%% ⚠ \figure{}{} MUST BE ON ONE LINE — paper.js matches it with a single-line
%% regex and silently drops a wrapped one, taking its \label with it.

The interesting question about a memory-safety bug is not whether it is
dangerous. It is what you would have seen in your logs. The corpus answers that
directly: every rung is run on every malformed input, and every run is
classified against the pattern's independent reference implementation.

\subsection{The adversarial protocol}

Each pattern ships malformed inputs aimed at its own bug —
\num{totals.plain_c.rows} of them across the corpus. Every rung is run on every
input at every build: \num{totals.adversarial_pairs} rung/input pairs,
\num{totals.adversarial_runs} executions, each classified against the model as
**matched**, **silent-and-wrong** (exit 0, wrong answer, no diagnostic),
**crashed** (a signal), or **never returned** (the timeout fired).

A rung does not always agree with itself, so the gate records one entry per
distinct behaviour with the builds that produced it: \num{totals.build_dependent}
rung/input pairs behave differently across optimisation levels or compilers, and
every one is a plain C rung \src{results/gate/*.json}. That forces an aggregation
rule, and the rule moves the numbers, so it is stated. The unit reported below is
a **row** — one pattern on one adversarial input, across both C compilers and all
four builds — and on \num{totals.plain_c.build_split} rows the same source on the
same input is silent in some builds and crashes in others. Both readings are
reported: silent-if-any-build-was-silent, and crash-if-any-build-crashed.

\subsection{The headline, and its denominator}

Take the plain, unchecked C rungs — `c-gcc` and `c-clang`, the two that carry
the bug — and ask, per row, what the worst thing they did was. Of the
\num{totals.plain_c.rows} such rows, plain C matched the model in every build on
\num{totals.plain_c.clean}; the remaining **\num{totals.plain_c.deviating}** are
the population worth reporting \src{results/gate/*.json}.

Of those, **\num{totals.plain_c.silent_first} are silent** — the program exits 0
and prints a plausible-looking wrong answer, with no diagnostic and no crash —
**\num{totals.plain_c.crash_silent_first} crash** and
**\num{totals.plain_c.hung} never returns**. Read crash-first, the same rows give
**\num{totals.plain_c.loud_first_silent} / \num{totals.plain_c.crash_loud_first} /
\num{totals.plain_c.hung}**. So silent failure outnumbers everything loud by
about three and a half to one under the first rule and about two to one under the
second — equally honest readings of the same rows, and silence dominates either
way. A finer-grained denominator exists — \num{totals.adversarial_runs} individual
runs, of which \num{totals.silent} are silently wrong — but it is dominated by the
rungs and inputs that behave, so the row-level figure is the one that answers
*"how often does this bug class hide"*.

\figure{outcomes}{The worst behaviour each rung produced on any adversarial input, counted over patterns. Every rung above plain C matches the model everywhere.}
\label{fig:outcomes}

\begin{caveat}{What the outcome matrix does not measure}
\ref{fig:outcomes} reads as "C corrupts memory, Rust catches it". That is not
what it measures, and the difference is the single most important caveat in
this paper.

The Rust rungs are the **fixed** program and the C rung is the **buggy** one.
The same rejection test that hardened C carries is present in every Rust rung
too, so on most patterns no shipped Rust rung ever reaches its own bounds check
on any input. Not one adversarial run, corpus-wide, ends with a rung refusing to
continue where the model says exit 0 (\num{totals.loud|plain} of
\num{totals.adversarial_runs}), and every non-zero exit a Rust rung produces
under attack is a driver-level input rejection — a short file, a capacity out of
range — that the C rungs produce identically \src{results/gate/*.json}. Not one
bounds check fires anywhere in the shipped matrix.

So the matrix largely measures a **design choice**: the bug was written in C
and not in Rust. Where safety is genuinely attributed, it is attributed by a
**deleted-check control**. On \pat{p02}, deleting the bound test from
`safe_naive.rs` and changing nothing else gives a program that prints C's
checksum bit-for-bit on well-formed input — the same program — and on the
one-byte overflow exits 101 with `index out of bounds: the len is 64 but the
index is 64` \src{patterns/p02-buffer-copy/NOTES.md}. That control is what
turns "Rust makes the check non-optional" from an assertion into a
measurement, and it is the only thing here that does.
\end{caveat}

Within those limits, \ref{fig:outcomes} shows where the deviation lives. Of the
corpus's \num{totals.cells_deviating} deviating (pattern, rung) combinations,
every single one is `c-gcc` or `c-clang`;
\num{totals.cells_clean_on_adversarial} combinations never deviate at all. Four
patterns are the reason plain C is not uniformly dirty, and they mark the
classifier's own blind spot: \pat{p01} has no bug to trigger, \pat{p08}'s
overlapping `memcpy` cannot misbehave on this box because glibc's `memcpy` *is*
`memmove`, \pat{p42} leaks memory, and \pat{p47} leaks through timing (clang
additionally matches on \pat{p38}, whose harm is an optimiser decision gcc takes
here and clang does not). The two leaks are real harms that never reach exit code
or stdout, so a classifier built on those scores them as "matched". Absence of
deviation in this matrix is not absence of a bug.

\begin{example}{A one-byte overflow that returns success}
\pat{p02} copies a length-prefixed record into a fixed 64-byte destination, and
`adversarial-cap1.bin` overruns that destination by exactly one byte. Plain,
unchecked C prints `198979479034752` and exits 0 in **seven of the eight** plain
C builds: the overflow lands inside glibc's chunk rounding, so nothing is
corrupted, nothing is detected, and the program returns a normal-looking number.
The eighth aborts — `gcc -O3` with whole-program inlining, where fortification
can see the allocation at the call — so as hardening that is one of eight builds
of one of three attacks \src{patterns/p02-buffer-copy/NOTES.md}.

The scope is narrow: one pattern, one input, one libc, and specifically the
*one-byte* case. p02's 65 535-byte overflow aborts loudly because it destroys the
next chunk header, and ASan fires on all three attacks when it is allowed to see
them. The realistic overflow is the invisible one; the spectacular one is the one
your monitoring already catches.
\end{example}

\subsection{What the detectors saw, and did not}

\begin{principle}{A silent detector and an absent detector are one observation}
A detector that reports nothing and a detector that never ran produce the same
log line, so no silence counts as evidence until the same tool, in the same
build, on the same box, has been shown reporting something. Every input here
declares in `model.py` whether the sanitizer must be clean or must fire, and on
a "fires" input silence is a gate failure. Across the corpus the sanitizer fired
on all \num{totals.sanitizer.declared_fires} inputs declared to require it and
was clean on the other \num{totals.sanitizer.clean} \src{results/gate/*.json}.
\end{principle}

Blindness here is not hypothetical. Each of the three detectors has a named,
measured blind spot in this corpus, and none of them is a bug in the tool.

**ASan, on a defect that never touches memory.** \pat{p18} decodes LEB128 and
shifts past the width of the type. Nothing is ever accessed out of bounds, so
ASan is silent on every input and every rung — the one pattern here whose
sanitizer row belongs to UBSan. The class needs stating precisely, because the
languages disagree about it: a width-overflow shift is **undefined behaviour in
C**, and in Rust an **arithmetic overflow** — a panic under `debug_assertions`,
and in release a defined masked shift \src{patterns/p18-varint-shift/NOTES.md}.
Four things catch it — UBSan, `-C debug-assertions=on`, Miri and Verus — and all
four are outside the built cell matrix, where safe Rust with the guard deleted at
`-O3` is bit-identical to C on every adversarial blob. Miri calls the Rust
program a **panic** rather than an `Undefined Behavior` finding, which is Miri
being right: there is nothing there to report. The defect was the *gate*, which
keyed on the UB flag and compared exit codes only where the model expected 0, so
a real Miri panic came back green. It compares both now.

**Everything, on non-termination.** \pat{p22} is an open-addressing probe loop
that never terminates on a full table. It is memory-safe: no bounds check to
fire, no lifetime to violate, no `unsafe` to point at. ASan and UBSan on the C
rung are silent — no diagnostic, no output, the process simply spins — and Miri
on a safe-Rust control with the guard removed did not terminate in 90 seconds
with nothing on stderr. Six safe-Rust cells hang, at both optimisation levels,
with zero `unsafe` anywhere in them \src{patterns/p22-hash-probe/NOTES.md}. This
is the corpus's only hanging row and it accounts for all \num{totals.hung} of its
never-returned runs.

**ASan, on the bug it is built for, because of hardening.** \pat{p08} performs
a genuinely overlapping `memcpy` and ASan says nothing. Fortification rewrites
the call to `__memcpy_chk`, and ASan's overlap check lives in its `memcpy`
interceptor, which is no longer on the path. Isolated to that one flag on
identical source: gcc at the box default is silent, gcc with fortification off
fires, and clang with fortification forced on goes silent the same way — so the
discriminator is the `_chk` symbol and not the compiler
\src{.memory/00-environment.md}. A hardening feature disabled a sanitizer check.

\begin{takeaway}
Your crash reports are not telling you about these bugs. The common case in
this corpus is a process that exits 0 with a wrong answer, and no supervisor,
core dump or alert will ever see it. And when a detector does run, remember
that **"no findings" and "the detector did not run" are the same log line**.
\end{takeaway}

\subsection{What this does not show}

Hardened C is correct on these inputs too — R1h as well as every Rust rung
matches the model on every adversarial input in every pattern that ships it
(\ref{fig:outcomes}) — so this corpus **cannot** distinguish "hardened C" from
"Rust" on outcomes, and any reading of \ref{fig:outcomes} as a language
comparison is reading it wrong. What Rust changes is narrower and, on this
evidence, real, and only the deleted-check control above measures it: the same
omission that gives C a silent one-byte heap write gives safe Rust a named,
immediate, non-exploitable abort.

Every rung above plain C holds the same obligation; what differs is who holds it
and whether they can forget.
