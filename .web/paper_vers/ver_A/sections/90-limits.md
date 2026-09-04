\section{What this cannot tell you}
\label{sec:limits}

Every number above measures a particular thing on a particular box, and the
distance between that thing and the question a reader actually has falls into
three families: what the instrument cannot see, what the unit distorts, and what
one box decides for you. Most of the items below are here because this project
was misled by them first.

\subsection{What the instrument cannot see}

**Nothing here is concurrent — not partially, not by accident.** For a large
part of this paper's audience, *"Rust is safe"* means fearless concurrency:
`Send`, `Sync`, and a compile-time answer to the data race. That result is not
in this paper, and it is not partially in it either.

\begin{caveat}{Zero of \num{totals.patterns} patterns model concurrency or data races}
No kernel in the corpus creates a thread. Across every C and Rust source under
`patterns/` there is no `std::thread`, no `pthread`, no `_Atomic` — and nothing
else in that family: no lock, no shared-ownership handle, no interior mutability
of any kind, no `unsafe impl Send`, no thread-enabling build flag, and no
ThreadSanitizer, helgrind or drd anywhere in the tree. Every kernel is a
single-threaded fold over a file blob, and every sanitizer report in `results/`
is from `thread T0`.
\end{caveat}

The two apparent counter-examples are not ones: `Sync` occurs once, as a rustc
`E0277` on a `static` in \pat{p36}, fixed by making the table a `const`; and
`Rc` and `RefCell` occur in \pat{p27}'s contract only inside its list of
forbidden spellings.

Concurrency was never *in* scope to be excluded from, either: the catalogue
keeps a table of axes the tree does not cover, names seven of them, and
concurrency is not among them \src{.memory/06-catalogue.md}. It was never on the
map, so nothing measured here bears on the guarantee most readers reach for when
they say the word *safe*.

**A green Miri row is one unpinned draw.** This corpus reports
\num{totals.miri_ub|plain} undefined-behaviour findings in
\num{totals.miri_runs} Miri runs, and that sentence is weaker than it looks: the
gate pins no seed and sets no `MIRIFLAGS`, so each run reports on whatever draw
the interpreter happened to make (\ref{sec:method}). Every Miri cell in this
paper, and every taxonomy row that rests on one, is a statement about a single
unrecorded draw under a single aliasing model — Stacked Borrows
\cite{stackedborrows20}, never Tree Borrows.

**Unsafe code at scale is not modelled.** Every one of the
\num{totals.tcb_items} trusted items here is declared in the same file as its
only caller, and nothing tests two trusted preconditions having to compose
across a module boundary, because no pattern is large enough to have two that
do. One of those items went wrong while every defence stayed green —
\ref{sec:proof} has it — and at three hundred sites across forty files that gets
harder to see, not easier.

**Coverage bias, and it runs one way.** The catalogue was written around bug
classes a cost ladder can *price*, so a class that safety prevents outright —
\pat{p08}'s overlapping `memcpy`, rejected before the program runs — has no
runtime check, and nothing in its cost column is the price of that rejection,
which makes the count of *"safety buys nothing
here"* entries in \ref{sec:hostile} a property of what was built rather than a
base rate. The same bias has bitten this project at the scale of a whole
document, in a form with no arithmetic signature at all, and \ref{sec:lies}
gives that episode. Read the entries. Do not read the tally.

\subsection{What the unit distorts}

**These are micro-kernels, and the honest consequence runs both ways.** The C
kernel files run from 16 to 124 lines. The blobs are large — up to 33 MB,
streamed — but the largest per-call working set in any pattern is 6 144 bytes.
Two of \num{totals.patterns} C kernels touch the allocator at all
(\pat{p27}, \pat{p42}); the rest allocate nothing in the measured
path, do no I/O and make no syscall.

**In one direction this strengthens the cost result.** Where the safety tax is
flat in the size of the data — \pat{p01}'s `+4…+5` instructions per call,
\pat{p02}'s `+11`, hardened C's own check at `+5` (gcc) and `+12` (clang) — it
is being measured against a kernel that does almost nothing else, so it is
appearing at its *largest possible* fraction. A per-call term that is already
invisible here is even more invisible inside a function that also parses,
allocates and logs.

**In the other direction nothing here licenses a claim about a real codebase.**
The fraction is entirely a property of what else the kernel does: \pat{p07}'s
binary search has nothing to hoist and nothing to amortise against, and its tax
is roughly half the kernel. A real program adds instruction-cache pressure,
branch-predictor contention and hundreds of other functions competing for the
same code layout — and \ref{sec:method}'s layout control shows that link order
alone can flip the sign of a rung comparison. In a real binary that is not a
controlled variable.

**The primary metric barely exists in the build you would ship.** Every headline
figure is `-O3`, inline mode `isolated`, which suppresses inlining so the kernel
keeps a symbol callgrind can attribute work to. In whole-program mode it is
usually inlined into `main` and has no symbol at all: of the 414 whole-mode
cell/input pairs at `-O3`, **394 have no kernel symbol**, and all 20 survivors
are gcc-built C cells carrying two different symbols, so no rung-to-rung
comparison survives there \src{results/synthesis.md}. That is not a defect of the
whole mode; it is what a real build does. The column
that would replace it is not comparable either: `main`-exclusive `Ir` counts
whatever else was inlined into `main`, which differs by language, and on
\pat{p01} that is about 12 M instructions the Rust `main` carries and the C
`main` does not — enough to report an 8% clang-over-rustc win that does not exist
\src{.memory/03-measurement.md}. **We cannot tell you what any of this costs in a
build where the kernel is inlined**, which is the build you would ship.

**\num{totals.patterns} patterns is a list, not a distribution.** The catalogue
is \num{totals.catalogue} rows and the built corpus is \num{totals.patterns} of
them, selected for mechanism rather than for frequency. Nothing here says which
bug classes cause the most real incidents, which are most exploitable once
triggered, or how often each occurs per thousand lines of C. Each row's
*mechanism* transfers; the ratio between rows does not.

\subsection{What one box decides for you}

**One box, one toolchain, one pin — and the negative results are the fragile
ones.** Everything is one container: 2× Xeon Gold 6230, glibc 2.39 with
`_FORTIFY_SOURCE=3` on by gcc's default, gcc 13.3.0, clang/LLVM 22.1.6, rustc
1.97.1 (whose LLVM is the same version, 22.1.6, separately built), and Verus
`0.2026.08.09.92f466f` with a pinned vstd. Every sentence of the form *"the
prover cannot express this"* is a fact about that pin, not about verification.

\begin{caveat}{"No specification exists" — published twice, wrong twice}
*"vstd has no spec for copy_from_slice"* stood for 44 tasks and propagated into
two patterns' source comments and one `.memory/` file; the pinned vstd specifies
it, with both a `requires` and a value-level `ensures`, and the false claim is
still alive in the gate's own docstring for the stage that tells an engineer to
write a twin. The same error recurred for `index_mut`. Both times the
specification was one directory away. \src{.memory/04-verus.md}
\end{caveat}

Read every *"the prover cannot express this"* here as *"we searched this pin and
did not find it"* — a weaker claim, and the one the evidence supports.

**One solver, one encoding.** Every proof result here is one SMT solver
\cite{z3} answering queries in the encoding Verus \cite{verus23} emits at one
pin; a different encoding, a different solver build or a different set of
quantifier triggers can turn a green run red, and nothing in this corpus varies
any of them. The \num{totals.tcb_items} trusted items counted in \ref{sec:proof}
are the surface this project *added*, not what a reader has to believe.

**The costs we did not measure are the ones migrations die on.** There is no
compile-time column; no proof-authoring time, though that is the dominant human
cost of \ref{sec:proof}'s top rung; no solver time, because `verus --time` is a
listed metric that no record in `results/` carries; no memory footprint; and no
maintenance cost for a kernel changing and its proof having to follow. There is
no cross-language binary size either, for a documented reason rather than an
oversight: rustc drops unused code from the shared driver before codegen while
gcc and clang link the whole translation unit, so adding one uncalled helper to
`common/driver.c` moved `binary_text_bytes` in 10 of 32 cells and **all 10 were
C** \src{.memory/03-measurement.md}. Migrations are abandoned over build times
and maintenance far more often than over instruction counts, and this paper has
nothing to say about either.
