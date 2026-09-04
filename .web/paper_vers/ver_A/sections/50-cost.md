\section{What safety costs}
\label{sec:cost}

%%literal-ok 230  p27's whole-program difference, not the trusted-line count
%% Owner: cost section, and ONE HOME for the 510x search-asymmetry retraction
%% and for the naive-rung median.  Every figure is kernel-exclusive `Ir` per
%% call at `-O3`, `isolated`, unless the sentence says otherwise.  Sources are
%% `results/synthesis.md` §2 and the named pattern's own NOTES.md.  The
%% pair-of-spellings rule LEADS the section: a hostile reader's exact complaint
%% was that the figures came first and the qualification last.

An engineer arriving at this corpus wants one number, and the corpus declines to
supply one. That refusal is not modesty: across \num{totals.patterns} patterns
and \num{totals.cells} measured cells the difference between a safe rung and an
unsafe rung ranges from exactly zero to roughly half the kernel, and about half
the time the quantity measured is not a safety check at all. What the corpus does
supply is a rule that predicts which case you are in — and, before that, the rule
that qualifies all of it.

\begin{principle}{Publish the pair, and name the side you did not search}
Every difference printed here is between two programs, and on almost every row
one of the two was searched for a cheaper spelling and the other was not: 14 of
\num{totals.patterns} patterns print `undeclared` in the project's own
search-state column, and nine report a real search on at least one side
\src{results/synthesis.md}. Where a side was searched, published differences
moved by up to 510× and changed sign on at least three patterns. The asymmetry
is structural — the unsearched endpoint is systematically the unsafe one, because
the prover's pin makes that side's levers expensive to try (\ref{sec:ladder}).

**Every safety-cost number ships as a triple: the number, the pair of spellings
it is a difference of, and which side was searched.** Without the other two
members it is a bound with one endpoint held by decree.
\end{principle}

\subsection{The decision rule}

\begin{principle}{Can the optimiser see the bound?}
A bounds check costs what the optimiser cannot delete. Where the fact that
discharges the check is already available to the middle-end — a clamp, a
modulus, a slice reborrowed once outside the loop, a length the caller already
tested — the safe rung's tax is a small per-call constant, flat in the size of
the data, and frequently exactly zero. Where the fact is only true and not
derivable, the check survives as a per-element cost that amortises along no
axis. So the question to ask of a candidate rewrite is not *"how many bounds
checks does it have"* but *"where does the bound come from, and does the
compiler get to see it there?"*
\end{principle}

\begin{example}{p03: handing the optimiser the invariant the proof proves}
The bounded stack, \pat{p03}, is the clean case, because the same lever is pulled
on both sides of the comparison and on two independent middle-ends. Its tuned
safe rung costs `+359` instructions per call on `small` and `+626` on `large`
against the unsafe rung \src{results/synthesis.md}. Add one provably dead line at
the top of the loop — `if sp > STACK_CAP { return 0; }`, which is exactly R5's
own invariant handed to LLVM as unreachable code — and the safe rung goes from 17
to 13 instructions per executed pop while the unsafe rung goes from 14 to 13. The
gap per pop becomes exactly zero, over 19 blobs, with zero fitted parameters and
a maximum residual of 0.0000 \src{patterns/p03-bounded-stack/NOTES.md}.

Two qualifications make it a result rather than a Rust anecdote. It is the
invariant specifically: `sp > 1000` changes nothing, and `sp > 65` leaves the
check standing and costs more. And it is not about Rust — clang keeps the
hardened C rung's check at 4 instructions per executed pop, but hand either clang
or gcc the identical clamp and both delete all of it. gcc shares no middle-end
with rustc, so the result licenses *"both compilers here, on two independent
middle-ends"* — not *"any compiler"*.
\end{example}

The corollary is that the source of the bound is often an operator, not a
language. On the ring buffer the elision rests entirely on `urem x, C`: the
operator hands LLVM's known-bits analysis the fact `x < next_pow2(C)`, and known
bits — unlike a range — survive the loop-carried phi. The access check disappears
exactly when `next_pow2(CAP) ≤ ARR_LEN` and no guard relates the two cursors — an
observed regularity with a mechanism attached rather than a theorem, which
predicted six configurations before they were compiled and is not closed under a
compiler version bump \src{patterns/p04-ring-buffer/NOTES.md}. The shipped row is
`+5 / +5`, flat; take the capacity from 64 to 60 and the same source, rungs and
compilers give `+479` on `small` — every figure at that capacity is that band,
because at 60 the larger blob starts rejecting pushes. On the fixed `strcat` the rule is *both ends*: a safe byte
loop with no bulk call in its source still lowers to `memcpy`, and checking only
the source per byte kills that lowering as dead as checking the destination
\src{patterns/p12-strcat-fixed/NOTES.md}.

\begin{example}{p07: the honest counterexample}
Binary search, \pat{p07}, has `Θ(log n)` probes, no inner loop, nothing to hoist
and nothing to vectorise; it is where the rule predicts a real tax. The tuned
safe rung costs 6.0000 instructions per probe more than the unsafe one, exactly,
with `probes = nq · ⌈log₂ n⌉`. Both rungs' per-probe costs are constants while
everything that could dilute the ratio is `O(1)` or `O(nq)`, so the tax rises as
a share of the kernel in both the array size and the query count: 42.53 % at
`n = 7` to 46.63 % at `n = 16 385`, still climbing, with an asymptote of
`6 / (12 + f_lo)` in `[46.15 %, 50.00 %]`, monotone across six deliberately
different workloads \src{patterns/p07-binary-search/NOTES.md}. If you want one
number for *"safe indexing where the optimiser cannot help you"*, it is this one,
and it is about half the kernel.


⚠ This is the paper's own rule applied to its own headline: \pat{p07}'s search
state is `undeclared`. Neither endpoint has been searched in contract, so the
figure bounds both sides rather than measuring either, and it is quoted here
because it is the largest honest tax in the corpus — not because it is settled.
\end{example}

\subsection{The spread is the finding}

\figure{rungcost}{Tuned safe Rust against unsafe Rust, one bar per pattern, at one input and one inlining mode. The spread — not the centre — is the finding: the same language pair produces near-zero, large-positive and negative differences depending on the kernel.}
\label{fig:rungcost}

\ref{fig:rungcost} plots the whole set; fourteen rows are below with what each
one is made of — tuned safe minus unsafe, with the licence and search-state
columns the project generates beside them \src{results/synthesis.md}.

| pattern | small | large | licensed? | search state | what the delta actually is |
|---|---:|---:|---|---|---|
| \pat{p22} | +2 | +2 | yes | R4 searched | a fixed-unsafe-rung bound; against another in-contract unsafe rung the same cell is +125 / +1021 |
| \pat{p04} | +5 | +5 | yes | undeclared | `urem`'s known-bits fact; at capacity 60 the identical source reads +479 |
| \pat{p02} | +11 | +11 | yes | undeclared | the check itself, flat in the copy length |
| \pat{p36} | +15 | +15 | undecided | **both sides searched** | the only row in the corpus with both endpoints searched |
| \pat{p17} | +32 | +32 | yes | R3 searched | one spelling, not a law: an in-contract respelling is −19 flat |
| \pat{p47} | +90 | +142 | yes | R4 searched, six levers | a constant-time discipline, not a bounds check |
| \pat{p27} | +110 | +662 | **no** | undeclared | out-of-line drop glue; the lifetime guarantee itself is 0 |
| \pat{p06} | +334 | +172 | yes | R3 searched, provisional | `zip`/`Rev` exhaustion tests; no safety in the per-byte term |
| \pat{p03} | +359 | +626 | yes | R3 partly searched | 0 per pop once the invariant is handed to the optimiser |
| \pat{p07} | +3015 | +10025 | yes | undeclared | a real per-probe check, 6 instructions each |
| \pat{p09} | +13756 | +48885 | yes | undeclared | the largest positive row here, and not decomposed in this paper |
| \pat{p13} | −177 | −1054 | yes | R4 searched | flips to +44 / +77 against a searched unsafe rung |
| \pat{p46} | −119 | −815 | yes | undeclared | one unrolling decision; the per-MAC safety tax is 0.00000 |
| \pat{p11} | −5768 | −24503 | **no** | R4 chained to the prover | not differenceable — only the safe side calls `CStr::from_bytes_until_nul` |

Over the 22 patterns whose safe-tuned-minus-unsafe row is licensed for
differencing, nine sit within ±32 instructions per call on both blobs, four are
negative on both, and nine exceed 100 on at least one. Those buckets do not
partition the rows, and the counts are of shipped spellings, which is what the
principle above is about \src{results/SYNTHESIS.md}.

\pat{p47} is in the table for a different reason: its row prices a constant-time
discipline rather than a bounds check, and the harm that discipline prevents is
quoted in instructions too. Two inputs differing only in *where* the first
mismatching byte falls take the same path through the constant-time rungs and
diverge by `+160` instructions through the leaking ones, at one and the same
checksum \src{patterns/p47-ct-compare/NOTES.md}. `Ir` is not time — that is
\ref{sec:method}'s point — but it is a sound proxy here, because the defect is an
early exit, which makes the leak a control-flow difference on secret data by
construction. One limit rides with that: *constant time* as a term of art
requires secret-independent control flow **and** addressing **and** no
variable-latency instruction on secret data, and this corpus exhibits the first
only.

\subsection{The same check costs about the same in C}

On the buffer-copy pattern the hardened C rung's check costs `+5` instructions
per call under gcc and `+12` under clang, and does not move between a 61-byte
copy and a 4092-byte one — 2.2 % and 5.4 % of the small call, 0.05 % and 0.12 %
of the large \src{patterns/p02-buffer-copy/NOTES.md}. The same pattern's tuned
safe Rust rung is `+11 / +11` against unsafe Rust, and the array sum's is
`+4 / +5`.

\begin{takeaway}
Writing the check costs roughly the same in both languages. What Rust changes is
not the price of the check but the possibility of forgetting it — and the
one-byte overflow of the previous section is what that difference buys.
\end{takeaway}

\subsection{What the rule looks like when it fires}

\begin{retraction}{The hash-probe safety tax is +2.00 per call, flat on every blob}
It was, for the pair of programs that shipped: `+2.00` on both blobs, one
distinct value across 32 of 32 blobs, past a fully green gate. A later review
wrote one further unsafe rung — the same kernel with the safe rung's single
reslice, keys still read through an unchecked accessor — which is in contract,
verifies at 20 items and 0 errors, and is byte-identical to its own proved twin
at `-O3`. Against that rung the difference is `+125` on `small` and `+1021` on
`large`: 510× the published figure on the large band
\src{patterns/p22-hash-probe/NOTES.md}.

What replaced it is not a corrected number. The standing rule is never to
re-ship a rung because a cheaper in-contract spelling turned up, so the cell is
published as a fixed-unsafe-rung bound with its counterpart beside it and
neither is called the true one. **Two minima are two upper bounds, and
differencing them bounds nothing in either direction**
\src{patterns/p42-goto-cleanup/NOTES.md}.
\end{retraction}

\subsection{Which safe rung you measure decides the answer}

The naive safe rung — the mechanical `for i in 0..n { v[i] }` port — is dearer
than the tuned one by a median of 7.26× across the 17 licensed rows whose safe
difference is positive on `large`, running from `−1.37×` to `3 536×`, with three
of the seventeen not overstatements at all. Applying the four searched unsafe
rungs collapses p22's ratio — the widest of the four with a searched unsafe
rung — from 1 033× to 2.02×, and leaves the median exactly
where it was \src{results/SYNTHESIS.md}. Quote the median, never the range, and
never a single row's ratio without its search state — and note that the naive
rung is what most published Rust-versus-C comparisons measure
(\ref{sec:ladder}).

\subsection{Large is not the same as bounds-checked}

Where the difference is big, name what you are paying for before calling it
safety. Three of the largest rows above turn out not to be safety at all, and
reading the instructions is what settled each; two are worth the space.

The handle table, \pat{p27}, looks like the price of a lifetime guarantee and is
not. Its `+230 / +793` whole-program difference — the one figure in this section
in that convention, because the decomposition is — splits into about `110` of
kernel, `120` of out-of-line Rust drop glue and `0` of allocator, with `malloc`,
`free` and all three Rust allocator shims equal to the last digit between the
rungs. The lifetime guarantee's own measured cost is zero
\src{patterns/p27-handle-table/NOTES.md}.

The rotate, \pat{p06}, is iterator bookkeeping: its `+334 / +172` is the
`zip`/`Rev` adaptor's two exhaustion tests per item, and decoding the surviving
panic pads puts eleven of them at identical source positions in three different
safe spellings and zero at any swap or fold site in any rung
\src{patterns/p06-rotate/NOTES.md}.

\begin{takeaway}
Three of the largest differences in this corpus are an unroll decision, drop
glue, and iterator-adaptor bookkeeping. Before attributing a measured gap to
memory safety, find the instructions and read them.
\end{takeaway}

The bounds check is not a cost the language adds. It is the price of moving an
obligation from the programmer to the compare-and-branch, and where the optimiser
can discharge it first, that price is zero.
