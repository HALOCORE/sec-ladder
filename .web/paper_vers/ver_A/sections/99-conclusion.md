\section{What is new, and what is already known}
\label{sec:related}

Everything above is one project's own measurement, and it rests on work the rest
of this paper never names. Prior work bounds the contribution in five ways: what
this paper assumes rather than shows, what is already measured at a scale this
corpus cannot reach, what defines the tools it leans on, what reaches further
than its ladder does, and what it has independently replicated.

**The premise is not ours.** The figure this whole exercise presupposes — that
roughly seven in ten serious security bugs in large C and C++ codebases are
memory-safety bugs — is reported independently by Microsoft's CVE triage
\cite{msrc19}, by the Chromium security team over its own bug corpus
\cite{chromium}, and by Android, which then watched the proportion fall as new
code moved into memory-safe languages \cite{android22}. This paper takes the case
for memory safety as given and prices one side of the trade.

**Unsafe code in the field is measured, and not here.** Three studies survey how
`unsafe` is used across thousands of published crates: what it is used for and
how it is encapsulated \cite{astrauskas20}, whether it is used safely
\cite{evans20}, and which memory- and thread-safety bugs real Rust programs ship
\cite{qin20}. That literature counts and classifies sites at a scale
\ref{sec:limits} concedes this corpus cannot reach; this paper prices one site to
the instruction and asks what a proof over it buys.

**What a Miri verdict means.** RustBelt \cite{rustbelt18} supplies the semantic
soundness argument under which a well-typed program calling verified unsafe
libraries is safe; Stacked Borrows \cite{stackedborrows20} is the operational
aliasing discipline Miri implements by default, and therefore the definition
behind every Miri cell in \ref{sec:quadruple}. Tree Borrows is the alternative
model and this corpus never ran it.

**The verifier.** The proof rung is Verus \cite{verus23}, SMT-backed
verification of Rust with linear ghost types, discharging its queries with one
solver \cite{z3}. Every ergonomic complaint in \ref{sec:proof} is about one pin
on one date and about the shape of value-level SMT verification, not about the
tool's design.

**Trace properties are reachable — by a different logic.** The taxonomy row
saying no proof here reaches \pat{p47}'s timing leak is a claim about the logics
on this ladder, and would be a naive one about proof in general. Constant-time is
relational, and relational verification reaches it: ct-verif reduces it to safety
on a product program \cite{ctverif16}, Jasmin combines a constant-time type
discipline with verified compilation \cite{jasmin17}, FaCT compiles a
timing-sensitive DSL \cite{fact19}, and a constant-time-preserving verified C
compiler \cite{compcertct} attacks the third failure named in
\ref{sec:quadruple} — that the back end chooses the machine code after the
prover has finished. Reaching that class means changing the logic, not
strengthening the specification.

**The layout result is a replication, and a stronger one.** That measured
performance can be dominated by accidents of layout is on the record
\cite{mytkowicz09}, and re-randomising layout is an established response
\cite{stabilizer13}. \ref{sec:method} adds a sharper instance: instruction count
and normalised function digest held identical, only the kernel's address moving,
and *every* rung-to-rung comparison in the control changing sign — confirmed out
of sample on 20 fresh symbol orderings whose predictions were hashed before any
timing. The refusal to quote a wall clock here is a replication with a mechanism
attached, not a local excuse.

**What is new is narrow.** Three things: each kernel written at six rungs and
measured cell by cell, with the proved rung pinned byte-identical to the unsafe
one, which turns *"the proof costs zero"* from an argument into a check; the
property-class × mechanism taxonomy of \ref{sec:quadruple}, every cell carrying
an instance from this corpus and vacuity separated from blindness by a control;
and the retraction ledger of \ref{sec:lies}, which is the part most likely to
transfer to a reader building a benchmark of their own.

**What would falsify the thesis.** The claim is that no rung discharges an
obligation — each relocates it — and that the residual is derivable from the
resource the new mechanism quantifies over. It fails if a mechanism can be
exhibited that removes an obligation outright, leaving no bearer, no quantifier
and no residual to name; or if two mechanisms agreeing on property, bearer and
quantifier are measured with different residuals; or if a residual derived in
advance from a stated quantifier is looked for and is not there. All three are
checkable against mechanisms this project never built, which is the point of
stating them.

**One confirmed prediction is not a predictive theory.** The gaps in
\ref{sec:hostile} were found by measurement, and the quadruple accounts for them
afterwards. Exactly one prediction was registered before its probe and then
confirmed, and one abstraction-led generalisation was written down by name and
refuted (\ref{sec:quadruple}). Read this paper as a taxonomy with one confirmed
prediction, and hold it to that.

\section{Conclusion}
\label{sec:conclusion}

Six rungs, \num{totals.patterns} kernels, \num{totals.cells} measured cells, and
the claim we set out to test in \ref{sec:intro} is the one that survived: **no
rung of this ladder discharges a safety obligation. Each one relocates it.** The
C rung leaves the obligation with the programmer. The safe rungs move it into a
compare-and-branch the compiler will emit whether or not it is needed. The
unsafe rung moves it back into a comment. The proved rung moves it into a
specification and a trusted base — and \ref{sec:proof} shows the residual there
is not zero but a different shape: what the prover quantifies over, and nothing
else.

Three results are worth carrying away.

**The cost of memory safety is not a quantity; it is a quantity of a pair of
programs.** \ref{sec:cost} shows the difference between two rungs moving by
orders of magnitude under a respelling that changes neither rung's semantics,
and about half the time the number a benchmark reports is not paid for by safety
at all. *"The bounds check costs X"* is almost never the right sentence; name
the mechanism instead, because the mechanism is what reproduces on inputs
nobody built.

**Memory safety is a specific property, and the specificity is measurable.**
\ref{sec:hostile} and \ref{sec:proof} collect the cases where every rung —
including the proved one — prints the same wrong answer: a bug that stays inside
the bounds, a read the program is entitled to make, a loop that never ends, a
leak in the timing trace under an identical contract. A proof discharges exactly
what it says, and the count beside it does not tell a reader what that was.

**The proof itself is free and the pin is not.** \ref{sec:proof} shows ghost
code erasing to byte-identical machine code; what costs is being confined to the
rungs the verifier can type, which is a price paid in the program you are then
allowed to write.

The transferable part is not any of those numbers. It is the quadruple in
\ref{sec:quadruple} — **property, bearer, quantifier, residual** — which is a
question you can ask of a mechanism this project never measured. Ask what
property is guaranteed, what bears the guarantee, what resource it quantifies
over, and what is therefore left outside it.

What is worth measuring next is what \ref{sec:limits} says is missing, in
order: **concurrency**, which this corpus does not touch at all and which is
what most readers mean by the word *safe*; the **interaction** between many
`unsafe` sites rather than a handful; and the costs a migration is actually
decided on — compile time, proof-authoring time, and maintenance when a kernel
changes and its proof has to follow. Until those exist, this paper prices one
family of obligations, on one box, for one pair of spellings at a time.
