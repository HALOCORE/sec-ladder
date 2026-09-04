\section{What this cannot tell you}
\label{sec:cantsay}

%% ⚠⚠ RULINGS.md R8: THIS SECTION MUST NOT END ON "WE CANNOT SAY". The ordering
%% by detector coverage is the payoff and it is mandatory -- the practitioner
%% reviewer rejected the plain "we decline to rank" version, and they were right:
%% it declines the one question a tech lead is paid to answer, immediately after
%% four demonstrations of new ways to be broken. ⚠ THE TAKEAWAY IS PROTECTED
%% (REVISE part E) -- do not trim it and do not reorder it.
%%
%% R6: every limitation ships with its DIRECTION. A bare "these are micro-kernels"
%% after a big claim reads as excuse-making and costs more trust than it saves.
%%
%% ⚠⚠ THE WALL-CLOCK LIMIT SHIPS WITH ITS COUNTEREXAMPLE (RULINGS R12 / REVISE
%% A3). A bare "instructions are not milliseconds" is a limitation without a
%% direction, which this paper's own rule forbids. The counterexample is
%% `.memory/03-measurement.md:403-409`: "gcc executed 10% fewer instructions than
%% clang on identical source and took 23% longer" (8765 vs 9764 Ir/call; 30.8 vs
%% 25.0 ms). Mechanism at :418-421 -- callgrind counts a `rep`-string instruction
%% once per repetition. What was withdrawn was two ROWS, not the column.
%%
%% ⚠ MIRI'S ALIASING MODEL IS NOT A RECORDED FACT (REVISE F15). `miriflags` is
%% `None` on all 26 gate records, so only the default ran and the tree never
%% records which model that was. Name it as the default; do not cite a model.
%%
%% The caveat's lead-in ("Nothing here is concurrent -- not partially, not by
%% accident", plus the `Send`/`Sync` framing) was CUT at the final trim: section
%% 1's concurrency paragraph is MANDATORY (R9) and said the same thing two pages
%% earlier, and the caveat's own heading carries the claim. The DIRECTION
%% sentence after the caveat is not part of that cut and must stay.
%%
%% The concurrency caveat is reused near-verbatim from ver_A 90-limits.md, which
%% the plan and the outline both call the most credible passage in the old paper.
%% Re-verified against the tree at writing time: no `std::thread`, no `pthread`,
%% no `_Atomic`, no `unsafe impl Send` anywhere under `patterns/`, and no
%% candidate row in `.memory/06-catalogue.md` proposes a race.

The question this paper has earned and cannot answer is *which of these do I fix
first?* Ranking bug classes needs two models and neither is here: how exploitable
each one is once triggered, and how often it occurs in real code.
\num{totals.patterns} patterns is a list, not a distribution — each row's
mechanism transfers to your code, the ratio between rows does not.

\begin{takeaway}
**One ordering does survive, read straight off \ref{sec:notdone}'s table: order by how many mechanisms in your toolchain can see the class at all.** A write outside the object is reached by four — a runtime bounds check, a sanitizer, Miri and a memory-safety proof. An index that is wrong but in bounds, a slot your own structure recycled (a reviewed probe, not a shipped pattern; Miri reported nothing) and a difference in instruction count between two inputs printing the same answer are reached by none. Fix by detector coverage first: that needs no exploitability model to be sound, and you can check it yourself with one known-bad input per class.
\end{takeaway}

\begin{caveat}{Zero of \num{totals.patterns} patterns model concurrency or data races}
No kernel in the corpus creates a thread. Across every C and Rust source under
`patterns/` there is no `std::thread`, no `pthread`, no `_Atomic` — and nothing
else in that family: no lock, no shared-ownership handle, no interior mutability,
no `unsafe impl Send`, no thread-enabling build flag, and no ThreadSanitizer.
Every kernel is a single-threaded fold over a file blob, and no catalogue row
proposes a race \src{.memory/06-catalogue.md}.
\end{caveat}

The direction of that gap is that it has none: if fearless concurrency is what
you are buying, nothing here is evidence for it or against it.

**Every other gap distorts in a direction you can name.** There is no wall
clock, and instructions are not milliseconds *in either direction*: on one
pattern here gcc executed 10 % fewer instructions than clang on identical source
and took 23 % longer — 8,765 against 9,764 instructions per call, 30.8 against
25.0 ms — and that pair is **unexplained**: this box has no hardware counters, so
the obvious mechanism cannot be tested. On a *different* pattern the same
direction disagreement does have a named cause, because callgrind charges a
`rep`-string instruction once per repetition and one x86 instruction can
therefore contribute thousands of counts — but that mechanism is explicitly ruled
out here, since this pattern's copies stay on the vector path
\src{.memory/03-measurement.md}. That is why \ref{sec:lied} withdrew two wall-clock rows for
a protocol defect and not the column. Inlining is suppressed in every build so
one kernel stays comparable across every rung, which makes each figure **an upper
bound on the cost in isolation**: per-call constants transfer to your code,
fractions of a kernel do not, because your function does other work. There is no
compile time and no proof-authoring hours, the costs migrations die on, so a
proof's price here is a floor. Unsafe code at scale is not modelled — every
trusted item is declared in the same file as its only caller, which is easier to
audit than any real codebase. And Miri's zero undefined-behaviour findings are
192 of \num{totals.miri_runs} attempted runs, two blocked at the 180-second
budget, no seed pinned, no flags set, its default aliasing model — which model
that was is the toolchain's choice and not something this tree records — and the
unsafe rung only: no safe rung here has been under it.

What would move this: a second box with a different libc, newer compiler and
prover pins, and one pattern whose bug is a race.
