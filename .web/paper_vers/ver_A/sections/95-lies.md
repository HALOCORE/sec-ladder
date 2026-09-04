\section{How this measurement lies to you}
\label{sec:lies}

%% ⚠ The out-of-sample retraction: "fake by residue" stays in FULL -- it is
%% concrete where the rank case asks the reader to hold an abstraction.  "Fake by
%% rank" is three sentences and must not grow back.

**Start with what held.** Every pattern here was built by one agent and then
attacked by a different one whose job was to break it. All
\num{totals.patterns} pass the gate with zero failures;
\num{totals.verus_verified} Verus items verify with
\num{totals.verus_errors|plain} errors and
\num{totals.verus_exit_anomalies|plain} exit anomalies;
\num{totals.adversarial_runs} adversarial runs over
\num{totals.adversarial_pairs} cell/input pairs produced
\num{totals.miri_ub|plain} Miri undefined-behaviour findings in
\num{totals.miri_runs} Miri runs — at one unpinned seed, as \ref{sec:limits}
qualifies. The mechanisms in \ref{sec:cost} and \ref{sec:proof} are what
survived that.

**What follows is what did not.** Nineteen published claims were retracted over
the life of this project \src{results/SYNTHESIS.md}. A ledger of nineteen reads
as instability, which is the wrong lesson; five are collected here because each
is a trap in the apparatus rather than a mistake about a pattern, and each would
recur in any benchmark of this shape — including one built by a reader who has
got this far. A sixth follows, because it is the only one with no arithmetic
signature at all. Two more live with the findings they correct rather than here
(\ref{sec:ladder}, \ref{sec:cost}), and that split is a policy: **a retraction
about the apparatus belongs where a reader can learn the shape of the trap; a
retraction about a number belongs beside the number.**

\begin{retraction}{The TLV walker's safety cost is O(n)}
It was written into the authoritative layer from an engineer's report,
**without re-measuring**, and corrected one review later. Taken as a difference
between two rungs spelled the same way, the per-byte tax is **zero** —
`0.00000 Ir` per folded byte, slope `0.0000000`, maximum residual `0.00`, over
127 consecutive record lengths at six fold spellings — and the mechanism is
visible in the listing: the reslice and the unchecked access both sit outside
the fold loop, so the chunk body is mnemonic-identical at every chunk width.

What made the error possible is that the claim rested on a **bare per-byte
rate**, and a bare rate is not a property of the kernel at all: this pattern's
own rate ranges `5.04688 … 6.62500` within its declared contract, one
exact-string substitution apart. The standing rule — never publish a safety-cost
claim without the tuned safe rung — was broken by the person who wrote the rule,
one pattern later. \src{RECAP.md}

**The rule.** Publish only matched-spelling differences — never a bare rate, and
never a difference of rates across unmatched spellings. And a summary of a
measurement is not the measurement: re-run the artefact rather than citing it.
The script named in this pattern's own notes as the evidence for mnemonic
identity prints `identical=False` at every width when re-run as committed. The
conclusion happens to be true; a reader of the citation could not have known
which.
\end{retraction}

\begin{retraction}{The law was validated out of sample}
Two hold-outs here could not have failed, in two different ways, and both
returned the perfect score that made them convincing.

*Fake by rank.* One pattern's leave-one-length-out reported
`max|residual| = 0.0` over 29 hold-outs, because its design stays rank 4 after
dropping any whole band: each hold-out re-derives the same exact solution, so the
test is arithmetically incapable of failing. A second pattern's held-out band is
a verified linear combination of the fit set's own extremes.

*Fake by residue.* \pat{p23} produced three mutually inconsistent closed forms,
each with zero in-sample residual. The published one mispredicted the pattern's
own shipped inputs by up to **152** `Ir` per call while its hold-out inside its
own band read `0.0000`. The missing term was a per-record function of `m mod 4`,
and every band sat at `m ≡ 0 (mod 4)`; the sweep sampled seven of eight
multiples of four. \src{.memory/03-measurement.md}

**The rule.** Report the post-drop rank beside any hold-out claim, and check the
residue class of every parameter your bands hold constant. **A residual of
exactly zero is not a strong pass; it is the signature of a test that could not
fail.** Only out-of-band prediction caught either failure — fit where two
parameters never co-occur, then predict the rows where both fire.
\end{retraction}

\begin{retraction}{The tables came back byte-identical, so nothing moved}
A field was added to 22 gate records, the published tables were regenerated, the
output file was byte-identical, and that was quoted as evidence nothing had
moved. It is byte-identical because the generator reads a different key: the new
field's name appears **zero times** anywhere in the generator. The control could
not have fired. Its neighbours on the project's own list of controls that could
not fire are the same shape — the shortest being a leak probe gated on `acc & 1`,
where `acc` is even on both of the inputs it was run against
\src{.memory/03-measurement.md}.

**The rule.** Before believing a check, ask what would make it fail — and then
make that happen. Ask, specifically, which single command carries a change from
the source all the way to the number a reader quotes. A test split across two
artefacts tests neither seam.
\end{retraction}

\begin{retraction}{The instrument can price only a compare-and-branch}
That sentence was the project's attempt to state its own instrument's domain —
the most useful kind of claim a benchmark can make — and the counterexample was
inside the report that made it. \pat{p38} prices a type-based aliasing property
at exactly `6.00 Ir` per call, agreed to the unit by five independent one-line
fixes, **none of them a compare or a branch, and one of them a compiler flag**
\src{results/SYNTHESIS.md}. Of the catalogue refusals a reviewer then re-audited,
eight stand with every load-bearing measurement reproducing exactly; one keeps
its verdict and loses its stated reason.

**The rule.** *Right verdict, wrong reason* — and the reason is what gets reused
on the next decision. A generalisation over a set of correct verdicts is a
separate claim needing separate evidence, and the first place to test it is the
cases you already have.
\end{retraction}

\begin{retraction}{The shipped binary is the slowest of 31 layouts}
\ref{sec:method} explains why this paper quotes no wall clock; this is the
retraction underneath it, and the failure is in the protocol rather than in the
physics. The probe gave each cell a contiguous block of every repetition instead
of alternating between cells, and the same effect **reproduced at zero layout
variation, on byte-identical copies** — that pattern's real noise floor is 5–45%
on identical binaries, wider than any gap read off it. Two patterns' wall-clock
rows were withdrawn, and two statistics with them: *worst-versus-best range* and
*dominance*, both extrema that do not converge as the population grows, and the
second introduced as the fix for the first \src{RECAP.md}. The hazard itself is
not new \cite{mytkowicz09}; \ref{sec:related} says what is.

**The rule.** Interleave by cell, never by block, and measure the noise floor
with byte-identical copies before believing any timing effect. Publish a
mode-matched comparison and a pairwise `P(A > B)` over the population; never
publish an extremum, and never repair one extremum with another.
\end{retraction}

\subsection{The one with no arithmetic signature}

The five above are all detectable: someone re-ran a probe, computed a rank, or
read a generator. The last is not, and it is why this section exists.

\begin{retraction}{The summary is faithful: every figure reproduces}
That was true, and it was not the question. When this project compressed
\num{totals.patterns} patterns into four results, its own review found the
omissions ran **systematically one way**. Five reviewed, quotable results went
missing and every one was flattering to safe Rust: the one-byte-overflow
security result, the constraint chaining the unsafe rung to what the prover can
express, an exact C-versus-Rust instruction match, and two more. Four smaller
ones went with them; all nine were restored.

The cause matters more than the incident. Nineteen retractions had trained this
project to distrust any headline saying *safety is cheap*, and the reflex then
deleted the evidence for it. The brief that commissioned the compression asked
for a section on where safe Rust does not help and contained no counterpart
item, so the asymmetry was built in before a word was written.
\num{totals.patterns} individually reviewed pattern cycles did not surface it;
one review of the aggregate did. \src{results/SYNTHESIS.md}

**The rule, and it is the hardest here.** **Coverage bias has no arithmetic
signature.** Every figure in the biased version reproduced correctly against the
record on the pass that found the bias — there was nothing to recompute, because
nothing was wrong. Checking a document's numbers cannot detect it. The only
check is a different question, asked of a finished document: **which way do its
gaps point?** If you have a well-drilled reflex against overclaiming in one
direction, audit your coverage in the other.
\end{retraction}

\subsection{What to do with this paper's own numbers}

**Read every figure as a bound with one endpoint held fixed by fiat**, for the
reason \ref{sec:cost} gives: on most rows one rung was searched for a cheaper
spelling and the other was not.

**Quote the mechanism, not the magnitude.** The transferable content of
\ref{sec:cost} is *why* a check survives or is elided — the dead clamp, the
capacity condition, the induction variable that does or does not already hold
the address being checked. Those reproduce on inputs the project never built.
The magnitudes belong to one box, one pin and one pair of spellings.

**And apply the sixth retraction to this document.** \ref{sec:limits} was
written by the same authors who chose what to put in \ref{sec:cost} and
\ref{sec:hostile}, and nothing in the gate checks which way a paper's gaps
point. That question is the reader's.
