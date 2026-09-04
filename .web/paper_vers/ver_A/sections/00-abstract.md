%% ver_A -- the abstract.  Corpus counts are \num, so they cannot go stale.
%% The scope-limit paragraph is non-negotiable; do not soften it.
%% ⚠ Gloss the obligation count, never bare: `N verified` counts items and
%% loops, not verification conditions.  ⚠ The C split and p07's share are
%% clauses without numbers; denominators live in sec:hostile and sec:cost.

\begin{abstract}
We built \num{totals.patterns} C micro-kernels — a TLV walker, a bounded stack, a
binary search — and implemented each at six rungs: unchecked C, hardened C, safe
Rust written naively, safe Rust written well, unsafe Rust, and unsafe Rust
carrying a machine-checked Verus proof. Each rung was built at two optimisation
levels and two inlining modes — \num{totals.cells} measured cells — each driven
against an independent reference implementation, hostile inputs, sanitizers, Miri,
and a byte-level identity check between the unsafe rung and its proved twin.
Verus reports \num{totals.verus_verified} items verified at
\num{totals.verus_errors} errors — a count of the functions and loops that
verified, not of verification conditions.

The thesis: *no rung discharges a safety obligation — each relocates it*, and
what is left over is predictable from the resource the new mechanism quantifies
over. The top rung is where relocation is easiest to mistake for elimination, so
it is the rung the paper proves the thesis on. A memory-safety proof buys memory
safety and nothing else: kernels here discharge every memory-access obligation
with zero errors and still serve an attacker a neighbouring caller's bytes,
return a wrong answer from an index they are entitled to form, or leak a secret
through timing under a contract whose obligation count never moves. The
obligation did not disappear; it changed bearer, and it changed units. The other
two results run the same way. Plain, unchecked C fails silently far more often
than it crashes, so its residual is one no crash reporter collects; and the price
of the language's check is a property not of the language but of whether the
optimiser can see the bound. The instrument that makes all three one story is the
**guarantee quadruple** — property, bearer, quantifier, residual — and the
paper's central artefact is a table of property classes against the mechanisms
that can and cannot reach each.

Two limits govern all of it. These are micro-kernels, not applications. And **no
pattern models concurrency or a data race** — every kernel is single-threaded —
so nothing here speaks to the guarantee much of Rust's audience means first.
\end{abstract}
