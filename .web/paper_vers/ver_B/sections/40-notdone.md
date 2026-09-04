%% ver_B section 4 -- THE SECTION WHERE THE ABSTRACTION IS EARNED. The words
%% arrive AFTER three programs have verified and broken. A future edit that moves
%% a definition above the failures has reproduced the defect that got ver_A
%% rejected. Authority: RULINGS.md > FACTS.md > OUTLINE.md.
%%
%% ⚠⚠ THE VOCABULARY IS THREE WORDS: property, bearer, RESOURCE (RULINGS R13 /
%% REVISE A4). It was four. `quantifier` was renamed: it collides with the
%% forall/exists reading for exactly the reader who would misread it, and
%% `resource` is the word the definition and the takeaway already used. The
%% coined noun `residual` is DELETED -- misused on first use (the value computed
%% is the RESOURCE), and colliding with the ordinary regression sense two
%% headline claims here use. What it said is now the takeaway's own consequence
%% sentence: whatever it does not range over is still your problem.
%%
%% ⚠⚠ THE STACK OVERFLOW IS DELIBERATELY ABSENT. DO NOT RESTORE IT. The outline
%% (beat 4.6) and `RECAP.md`'s "family of three" carry a `decreases` clause that
%% verifies while the binary dies of stack overflow. Two agents went to the
%% primary artefacts and the evidence is not there: no such pattern (a REFUSED
%% candidate), no `overflowed` in the logs, no verifier in the build script, the
%% source untracked, and the probe's own report saying its verified function "is
%% a different function, not the same kernel". RULINGS R1.
%%
%% ⚠⚠ THE BITSET CONTRAST RUNS THE OTHER WAY FROM WHAT THIS FILE USED TO SAY
%% (RULINGS R10 / REVISE A1). `patterns/p09-bitset/NOTES.md:872-876`, verbatim:
%% "the bounds check and the sanitiser catch `q >> 5` on an input nobody would
%% think to write, and never on the five shipped ones; the proof catches it on
%% every input, because its obligation is universally quantified." The panic and
%% the ASan report exist ONLY on `.temp/p09/thin.bin`. The old wording demoted
%% the one mechanism that generalised.
%%
%% ⚠ THE RANGE PARSER HAS THREE PARTS AND ALL THREE SHIP (RULINGS R7-CORRECTED).
%% (1) On the CROSSWIN PAIR -- two committed files differing only in the victim's
%% 28 secret bytes -- the shipped, plain-C rung DISCLOSES, ASan silent, no panic,
%% exit 0, and it is in the committed gate record. (2) On `adversarial-leak` the
%% excess bytes are the attacker's OWN request table: a wrong answer, and saying
%% otherwise re-ships a claim corrected at TASK_011_REVIEW. (3) The memory-safe
%% Rust and Verus programs that leak the same bytes are CONTROL VARIANTS.
%%
%% ⚠ The bitset's `19 verified, 0 errors` is the functional-spec-STRIPPED
%% configuration WITH one bit-vector hint line; bare it is `17 verified, 1
%% errors`. Both halves stay. RULINGS R6. And redefining `word_of` to /128 alone
%% is `17 verified, 2 errors` -- 20/0 needs the BRIDGE LEMMA moved too (REVISE
%% F9); the old text attributed 20/0 to the one-line spec edit and that is wrong.
%%
%% ⚠ The constant-time leak is +7088 Ir/call, and on THIS pattern `Ir` is not a
%% proxy for the harm -- `p47/README.md`: "it *is* the harm". What licenses that
%% is determinism ("`Ir` is a deterministic function of the input, and a leak is
%% exactly a dependence of a resource on a secret"); a constant count is
%% NECESSARY, not sufficient; and there is still no wall-clock measurement of it
%% in the tree, so never write "leaks through timing" bare (REVISE F12).
%%
%% ⚠ The goto-cleanup ghost ledger (a postcondition published as stating
%% leak-freedom that still verifies `18 verified, 0 errors` after the release on
%% its error path is removed) was CUT FOR LENGTH at the final trim: its
%% conclusion -- somebody has to read the trusted lines -- is carried by the
%% example below and by \ref{sec:close}. If it is ever restored it may appear
%% ONLY as that one prose sentence in the trusted-base paragraph (RULINGS R5),
%% and must NOT be extended into a claim that a prover cannot express a resource
%% property: `.memory/04-verus.md` forbids that claim and the question is open.
%%
%% ⚠ TABLE GRADING (REVISE F14). A cell is `no` only where the mechanism's OWN
%% rule was violated and it stayed quiet. Apply that and no cell qualifies, which
%% is the section's own argument arriving as a measurement. The `—` cells on the
%% self-recycled row are honest: that probe carried no Verus rung, and p27's
%% `spec.md` ARGUES `PointsTo` would license the stale read -- an argument is not
%% a measurement. It is a reviewed probe, not a shipped pattern; label it.
%%
%% ⚠ TWO TRUSTED-BASE ATTACKS, BOTH STOPPED (RULINGS R11 / REVISE A2). The
%% `i <= v@.len()` weakening passed at TASK_008_REVIEW; the twin added at
%% TASK_009 now rejects it. The `copy_nonoverlapping` substitution is caught by
%% the O3 identity pin and Miri. Presenting either as a live hole tilts the paper
%% against the verifier -- §6's own failure, pointing the other way. Do not
%% "balance" this back.

\section{Proved is not done}
\label{sec:notdone}

The migration lands. The parser is safe Rust now, and where it had to stay
`unsafe` there is a machine-checked proof that printed `0 errors`. Someone asks
whether the bug class is gone. The obvious answer is yes: memory-safe means
safe, proved means correct. **Three programs here verify with zero errors and
are broken anyway.**

**The first is one character wide.** A bitset probe indexes its backing array
with `words[q >> 6]` — sixty-four bits to the word. Type `q >> 5` and the index
overshoots, and on the five inputs this pattern ships **only the proof sees
it**: the panic and the ASan `heap-buffer-overflow` appear on one probe blob
built narrow enough for the overshoot to leave the allocation, and on nothing
anybody would ship. The proof catches it on every input, because what it must
discharge is a claim about every index rather than a sample. Now type `q >> 7`.
Dividing by 128 never exceeds dividing by 64, so under the same guard the index
is always a legal word — the wrong one — and **nothing catches it on any input,
because no such input exists.** One byte differs in the 368-byte kernel, so the
bug is free; ASan, UBSan and Miri report nothing and exit 0 on a wrong checksum;
and the prover, with the functional postcondition stripped, reports `19 verified,
0 errors`, a row needing one bit-vector hint line — bare it is `17 verified,
1 errors`.

Now the part that should worry you. That pattern's functional postcondition does
catch this bug — so move it. Redefine the specification's word-index function to
divide by 128, matching the shift the author typed, and Verus reports
`17 verified, 2 errors`: a bridge lemma inside the proof is now false. Move the
lemma too and it is `20 verified, 0 errors` — a program proved to meet a
specification that *is* the bug. \src{patterns/p09-bitset/NOTES.md}

**The second reads another client's bytes through a bounds check that holds.** A
range parser mirroring a real HTTP server flaw is handed a whole response
buffer, not just its own window. Its two committed cross-window inputs differ in
nothing but 28 bytes of a neighbouring window's secret, and **plain, unchecked C
prints a different checksum on each** — exit 0, no panic, no sanitizer report.
Weaken the Rust guard by one token, bounding the start against the slice rather
than the window, and every access is still inside the slice, so every
memory-safety obligation — every claim the prover must discharge — is met at
`10 verified, 0 errors` with the functional postcondition stripped, and those
control variants, memory-safe and proved, disclose the same bytes the C rung
did. What catches it is the *functional* postcondition, never the access one:
with the functional spec present, `9 verified, 1 errors`. Two things this is
not. Plain safe Rust with no `unsafe` and no proof discloses those bytes too, so
it was never a claim about verification; and on the single-window input the
excess bytes are the attacker's own request table — a wrong answer, not a
disclosure. \src{patterns/p17-http-range/NOTES.md}

\begin{principle}{A bounds check bounds the slice you were handed}
Hand a parser the whole buffer and "in bounds" spans every other client's data
in it. Rust enforces that bound perfectly and the leak goes straight through
it. Pass the narrowest slice, not the buffer.
\end{principle}

**The third leaks through a contract it satisfies to the letter.** In a
verified constant-time tag comparison, replace the or-accumulating loop with an
early-exiting one plus a lemma saying the accumulator is sticky: Verus reports
`14 verified, 0 errors`, the **kernel's** own obligation count unchanged at 3,
no character of `requires` or `ensures` different. Two inputs printing the same
checksum then differ by **+7,088 instructions per call** — and on this pattern
that count is not a proxy for the harm, it *is* the harm, because executed
instructions are a deterministic function of the input and a leak is exactly a
dependence of a resource on a secret. A constant count is necessary and not
sufficient, and no wall-clock measurement of it exists here. The contract
denotes the **value** returned, and both kernels return it.
\src{patterns/p47-ct-compare/NOTES.md}

Those proofs were not weak: the leaking comparison discharges the identical
contract the honest one does, and the bitset's index really is inside its
array. So *is it safe?* is the wrong question. **Three words follow, as the
shortest thing that tells those three programs apart.**

**Property** — which predicate, not "is it safe". *Every read is inside a live
allocation* and *the result folds the bytes the request named* are different
sentences, and the range parser satisfies only the first. **Bearer** — who
establishes it: a comment, a compile-time check, a runtime compare-and-branch, a
solver, an interpreter, the operating system, or nobody. **Resource** — what the
guarantee ranges over: values, the execution trace, allocations through *this*
allocator, stack frames, wall-clock time. The third is load-bearing and the one
always missing.

The three failures ladder by it: the bitset's guarantee never ranged over the
**value computed**, the parser's never over **the data you were handed**, the
comparison's never over the **execution trace** — each a step further from
anything a bounds check could have covered.

They paid predictively once. A handle table's proof rests on a permission
`deallocate` consumes, so it ranges over *records released through this
allocator* — and a structure recycling its own slots releases nothing. A reviewed
probe, not a shipped pattern, agreed: use-after-recycle and slot double-free are
both writable in safe Rust and silently wrong, with **Miri reporting nothing**.
\src{.memory/01-ladder.md}

\subsection{Which of your mechanisms reaches which bug class}

| bug class | rustc's types | a runtime check | ASan / UBSan | Miri | memory-safety proof | full proof |
|---|---|---|---|---|---|---|
| a write outside the object | nothing to find | **yes** | **yes** | **yes** | **yes** | **yes** |
| in bounds and the wrong index | nothing to find | nothing to find | nothing to find | nothing to find | nothing to find | yes, until the spec inherits the bug |
| use-after-free through the allocator | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| use-after-recycle in storage you own | nothing to find | nothing to find | — | nothing to find | — | — |
| timing and information flow | nothing to find | nothing to find | nothing to find | nothing to find | nothing to find | nothing to find |
| non-termination | nothing to find | yes, a watchdog | nothing to find | nothing to find | nothing to find | **yes** |

`yes` reaches the class with a measurement behind it; `nothing to find` is
silent because nothing there violates *that* mechanism's own rule; `—` is not
measured. **No cell reads "silent, and it should have seen this", and that is
the result**: not one of these silences is a tool failing at its job. Each is a tool
asked a question it does not ask, which is why adding another sanitizer does not
help and naming the property does.

\begin{caveat}{Every column is one mechanism at one version, not a mechanism class}
A linear or session-typed language reaches the self-recycled row rustc does not;
relational verification is built for the timing row this prover at this pin does
not reach \cite{ctverif16} \cite{jasmin17} \cite{compcertct}. Read every silence
above as *this tool, this version*, never as *nobody can*.
\end{caveat}

\subsection{What you are still trusting after it verifies}

On its shipped rungs this corpus verifies \num{totals.verus_verified} items —
functions, loop bodies, `by(...)` sub-proofs, not verification conditions —
standing on \num{totals.tcb_items} hand-written trusted items over
\num{totals.tcb_lines} lines the verifier never checks (\ref{fig:tcb}).

\figure{tcb}{Per pattern: items verified, hand-written trusted items, the lines inside them, and the verified twins behind them.}
\label{fig:tcb}

Those lines are axioms about the world, and weakening one is silent and
non-local. Two attacks have been run on them, and **both were stopped from
outside the prover**. Substituting `copy_nonoverlapping` for `copy` inside a
trusted body whose whole contract is the non-overlap verifies at `11 verified,
0 errors` while committing that pattern's own undefined behaviour — invisible to
Verus and to its verified twin, caught by the `-O3` identity pin against the
unsafe rung and by Miri. Weakening a trusted accessor's `i < v@.len()` to
`i <= v@.len()` passed a full green gate when first tried; a *verified twin* —
the same contract reimplemented in checked code, re-run every gate — was added
afterwards and now rejects it. Neither mechanism is the prover, and on your own
code you would build both yourself. Four sinks go uncounted besides: the solver
\cite{z3}, the encoding of Rust into SMT \cite{verus23}, rustc's ghost erasure
and LLVM, and the pinned standard library's axioms.
\src{.memory/04-verus.md}

\begin{example}{The escape hatch the verifier offers you}
When Verus rejects a call it prints a suggestion: paste this
`assume_specification`. The printed form has **no `requires` and no `ensures`
at all**, and a program built on it verifies a 1 MiB out-of-bounds read and a
null dereference at `4 verified, 0 errors` — the largest single-line hole a
trusted base can have, offered when you are least inclined to argue. No rung
here contains one; that is a decision somebody made, not a property of the tool.
\src{.memory/04-verus.md}
\end{example}

None of that makes a proof a bad purchase, and stopping here would let this
section's gaps run one way. **A proof costs zero executed instructions**:
proved and unproved kernels are identical machine code at `-O3` on
\num{totals.identity_exact} of \num{totals.patterns} patterns, and on the one
exception zero executed instructions still holds, what differs being a
trait-declared ghost function in a vtable slot. **It costs about four times the
source text**: \num{totals.proof_text.ratio_pct} % of the unsafe rung's lines,
raw lines including comments and blanks, so it measures file size and not proof
effort. **And it held under attack**: its preconditions are now your debt, and
they were satisfied on all \num{totals.proof_domain.inputs} inputs over
\num{totals.proof_domain.calls} calls, adversarial included.

\begin{takeaway}
Before trusting any safety mechanism — a language's, a sanitizer's, a prover's
— write down the **resource** its guarantee ranges over. Whatever it does not
range over is still your problem, and you can name it before you run anything.
\end{takeaway}
