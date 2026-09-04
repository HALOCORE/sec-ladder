\section{What a proof buys, and what it does not}
\label{sec:proof}

%% Owner: proof section. Authority: `.memory/04-verus.md`, which supersedes
%% RECAP, SYNTHESIS and the pattern's own NOTES.md — and which carries the
%% TASK_116 retraction of p42's ghost ledger that NOTES.md has not yet landed.
%% ⚠ p42's ghost ledger is told IN FULL in sec:quadruple; here it is the
%% count-invariance instance only.  ⚠ p11's refused CStr rung is sec:ladder's.

The proof at the top of this ladder is free in executed instructions and in
nothing else. This section charges it in three other currencies — the proof text,
a trusted base, and the programs the prover will not let you write — and then
asks what the resulting figures certify. The two numbers a paper of this shape
reports, items verified and trusted items counted, are the two most reliably
over-read.

\subsection{The proof costs zero executed instructions}

The top rung is the rung below it with its unsafe preconditions discharged, and
the discharge is free at run time in the strongest available sense: the proved
and unproved kernels are byte-identical machine code on
\num{totals.identity_exact} of \num{totals.patterns} patterns at `-O3`, checked
on the raw bytes of the kernel symbol rather than inferred from an instruction
count (\ref{fig:identity}) \src{results/synthesis.md}.

\figure{identity}{Byte-level identity between the unsafe rung and the proved rung, and the corpus-wide obligation count beside it. The instruction-count equality is entailed by the digest equality, not independent evidence for it.}
\label{fig:identity}

The remaining pattern is identical once pc-relative displacements are masked, and
its exception is the scope clause on *"ghost code fully erases"*: a `spec fn`
declared in a trait is codegenned as a stub and takes a vtable slot, so the
proved binary's vtables are 40 bytes to the unproved one's 32
\src{patterns/p36-vtable-dispatch/NOTES.md}. Zero executed instructions holds.
*Byte-identical* does not.

\subsection{But "the proof costs zero" is not "verification is free"}

**(a) The proof text.** Across all \num{totals.patterns} patterns the proved
sources total \num{totals.proof_text.verus_lines} lines against the unsafe rungs'
\num{totals.proof_text.unsafe_lines} — an aggregate ratio of 4.0×, a median of
4.2×, from 2.6× on the state machine to 6.3× on the buffer copy. Whole-file
counts including driver and specifications, which is the honest unit: it is what
someone maintains to keep the machine code the unsafe rung already had.

**(b) The trusted base.** \num{totals.tcb_items} hand-written trusted items over
\num{totals.tcb_lines} lines carry bodies the verifier never checks — distinct
counts rather than column sums, since every pattern includes the same shared
driver \src{results/synthesis.md}. That is the *project-local* trusted base and
not the trusted computing base, a distinction taken up below and larger than the
number.

**(c) The programs the prover forbids.** An admissible unsafe rung must be one
the pinned Verus can express, because the gate holds it byte-identical to its
proved twin; cheaper spellings were built, measured and refused on several patterns
for that reason alone, one of them worth `−17 526` instructions per call
(\ref{sec:ladder}) \src{patterns/p11-nul-scan/NOTES.md}.

\begin{caveat}{The unsafe rung is held above its floor}
The pin that makes *"the proof costs zero"* checkable is the pin that holds the
unsafe rung above its floor. So *"what a proof costs"* is two numbers: zero
instructions for the proof, and whatever the pin's expressiveness costs you in
the rung you are then permitted to write — priced here only where somebody built
the excluded rung and measured it.
\end{caveat}

\subsection{A proof alone buys nothing; it has to license unsafe code}

\pat{p01} ships the control that settles this. Its naive safe rung was given the
same Verus proof the unsafe rung gets — no `unsafe` token anywhere, a smaller
trusted base of 5 lines across 2 items — and came out byte-identical to the
*unproved* safe rung at both optimisation levels: 49 static instructions against
the unsafe rung's 36, and 11 to 29 more executed per call
\src{patterns/p01-array-sum/NOTES.md}. Proving a safe rung panic-free leaves every
bounds check standing, because rustc never learns what the solver knew.

\begin{principle}{A proof pays only where it licenses something}
Verification is not an optimisation. It removes no check that the compiler was
going to emit; it authorises you to have written code that never had one. A
proof attached to a rung that was already safe buys assurance and costs
instructions.
\end{principle}

\subsection{What the obligation count counts}

\begin{principle}{The obligation count is not a coverage measure}
Do not report how many obligations a proof discharges as though it told a reader
what the proof covers. Report which properties are stated, and pin the contract
textually so that deleting one is visible.
\end{principle}

\num{totals.verus_verified} items verified at \num{totals.verus_errors} errors is
the number a paper of this shape reports, and it is not what the word suggests.
Verus's `N verified` moves by one per function, one per exec loop body, one per
`by(…)` sub-proof and one per `const` inside `verus!` — a checksum over the
function-and-loop skeleton \src{.memory/04-verus.md}. In this field a *proof
obligation* is a single verification condition, and one of Verus's units can
carry arbitrarily many, so reported as an obligation count the number overstates
granularity by a factor nobody here has measured.

It is also invariant under the weakenings that matter. Put the timing leak back
into \pat{p47}'s proved rung and the kernel's own count stays at 3, `requires` and
`ensures` not one character different between the honest file and the broken one
(\ref{sec:quadruple}). Deleting a *kernel's* `requires` fails — deleting a
*trusted item's* cannot, since that only removes obligations from its callers: on
the buffer copy, deleting a trusted precondition, or replacing both with the
tautology `n >= 0`, each leaves the count at 9 verified, 0 errors.

The strongest instance cost this project a published claim. \pat{p42}'s proved
rung escrows its deallocation permission in a ghost ledger and `ensures` the
ledger comes back empty on every exit, published as stating leak-freedom. Delete
that `ensures` and the file still reports `18 verified, 0 errors`; so does a
one-line ghost drop that leaks `n_err × win_len` bytes, at an unchanged twin and
axiom count, its `-O3` kernel byte-identical to the shipped unsafe rung
(\ref{sec:quadruple}) \src{.memory/04-verus.md}. Green gate, reproducing record,
matching pinned count, holding identity pin, false central claim. Nothing in a
count — nothing in this gate — checks that an `ensures` means what its prose says.

\begin{example}{A published CVE, verified, still serving somebody else's bytes}
\pat{p17} ports CVE-2017-7529, nginx's range filter. `Range: bytes=-N` makes the
start offset negative in signed arithmetic, the only validation is
`if (start < end)`, and a negative start passes it. The read never runs *past* the
window — it runs backwards, and how far back is one attacker-controlled `u16`
\src{patterns/p17-http-range/NOTES.md}.

Change one token in the proved rung's guard, bounding the start against the whole
blob rather than against this window, and strip the functional postcondition —
not a second bug but the probe, the way to ask whether the memory-safety half
stands alone. Verus reports `10 verified, 0 errors`. Run that binary on two
128-byte inputs identical except for a neighbouring window's 28 secret bytes and
it prints two different checksums. Every memory-safety obligation discharges,
because every read is inside the allocation.

Two controls say what did it. The verified program is **not** `unsafe`-free — it
carries the pattern's one trusted accessor — but a zero-`unsafe` variant, plain
safe Rust bounds-checked on every access, discloses the same bytes, so the
accessor is not the cause. And the sanitizer silence is a result about the **C**
rung, where the model declares that input clean on purpose: a sanitizer that
*had* fired would have failed the gate.
\end{example}

\subsection{The trusted base is where the guarantee lives, and it is fragile}

\begin{principle}{A trusted precondition is an axiom about the world}
Every `external_body`, `assume_specification` or hand-written contract is an
axiom, and weakening one is silent and non-local. Count them, classify them, and
say in words how the code reaches memory — a small number is not by itself a
small trusted base.
\end{principle}

\figure{tcb}{Per pattern: obligations discharged, hand-written trusted items, the lines inside them, and the number of verified twins standing behind those items.}
\label{fig:tcb}

**The count in \ref{fig:tcb} is the project-local trusted base, not the trusted
computing base.** It is what *these authors* wrote and asked you to believe
unproved. Every R5 result also rests on four trust sinks nobody counted: **Z3**,
whose `unsat` is taken as a proof; **Verus's encoding of Rust into SMT**, where a
mis-modelled aliasing, arithmetic or ownership rule would give a green run over
an unsound argument and no stage of this gate would notice; **rustc's
ghost-erasure pass and LLVM**, which choose the machine code *after* the proof
finishes — a trust \ref{sec:quadruple} shows to be misplaced for at least one
property; and **the pinned standard library's own axioms**. None of the four is
verified or measured here, and in this field *"trusted computing base"* names
exactly that list.

Two measured attacks say what the counted number does not protect. **A proof of a
precondition is not a proof that the body honours it**: substitute
`copy_nonoverlapping` for `copy` inside \pat{p08}'s trusted `move_right`, a body
whose entire safety contract is the non-overlap, and it verifies at 11 items, 0
errors while committing the pattern's own undefined behaviour. **A precondition
can be too weak by one character**: weakening a trusted accessor's
`i < v@.len()` to `i <= v@.len()` passed a full green gate — not a tautology, so
the tautology probe missed it; both parameters present, so coverage missed it —
leaving the trusted base to axiomatise that reading one byte past the end of a
slice is defined \src{.memory/04-verus.md}.

\subsection{How the base is defended, and the hole in each defence}

| defence | what it checks | measured hole |
|---|---|---|
| count body lines | size of the unchecked surface | nothing about strength, and gameable prospectively: a rung on verified raw pointers needs zero project-local items |
| tautology probe per `requires` | that the clause constrains some caller | judges triviality, not strength; `i <= v@.len()` passes it |
| delete each `ensures` in turn | that the clause is load-bearing | tests `ensures` only, and the dangerous hole is in `requires` |
| a verified twin per trusted item | that a checked implementation meets the same contract | catches a weakened `requires` and only that; the `copy_nonoverlapping` substitution passes it cleanly |

The twin judges strength, and the transferable part is why: **a twin's value is
that it fails when the precondition is deleted.** A `requires` too weak to
license the unchecked operation is too weak to license the checked one, and a
twin that still verifies without it never used it \src{.memory/04-verus.md}.

\begin{caveat}{Never publish a zero in the local-axiom column bare}
The corpus declares \num{totals.axiom_decls} pattern-local axioms, and all
\num{totals.patterns} proved sources carry `broadcast use` — one vstd group alone
is six hand-written `broadcast axiom fn`s in the pinned standard library. Every
number in this paper rests on hand-written axioms. They are the standard
library's, pinned, and outside the column by construction, so a zero says *"this
pattern's author wrote none of their own"* \src{results/synthesis.md}.
\end{caveat}

\begin{example}{The escape hatch the verifier offers you}
When Verus rejects a call it prints a suggestion: paste this
`assume_specification`. The form it prints has **no precondition and no
postcondition at all** — no `requires`, no `ensures` — and a program built on it
will verify a 1 MiB out-of-bounds read and a null dereference at `4 verified, 0
errors`. The tool's own convenience feature is the largest single-line hole in any
trusted base here, offered at the moment you are least inclined to argue with it.
\src{.memory/04-verus.md}
\end{example}

\begin{takeaway}
A proof discharges exactly what it says, over exactly the resource its
obligations quantify over. A memory-safety proof quantifies over addresses, so a
kernel that reads only addresses it is entitled to read satisfies it while
leaking a secret. The proof does not remove the obligation either: it moves the
obligation into a specification and a trusted base, and \ref{sec:quadruple} is
about how to tell what is left there.
\end{takeaway}
