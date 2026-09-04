%% ver_A section 8 -- THE CORE. Every cell is backed by a verus.rs header, a
%% NOTES.md control table or SYNTHESIS; unmeasured is a dash. ⚠ Columns name ONE
%% mechanism at ONE version -- the "Columns" note is load-bearing. ⚠ p42's
%% Full-proof cell is `no` per `.memory/04-verus.md` (TASK_116), which supersedes
%% the pattern's NOTES.md and RECAP on the ghost ledger.

\section{The guarantee quadruple}
\label{sec:quadruple}

\ref{sec:proof} left two programs that verified and were broken anyway: a
constant-time comparison that leaks, and a cleanup path whose proof does not
cover the leak it exists to model. A third belongs with them and is stated here
rather than there because it is ⚠ **provisional and unreviewed** — a recursive
kernel whose `decreases` clause verifies at `3 verified, 0 errors` while the
binary dies of stack exhaustion \src{RECAP.md}. The tempting reading is that
those proofs were weak. They were not — the leaking comparison discharges the
*identical* contract the honest one does — so something other than proof strength
is doing the work \src{patterns/p47-ct-compare/NOTES.md}.

A safety mechanism does not make a program safe. What it does is narrower and
mechanical: it **binds a proof obligation to a bearer, over a stated quantifier,
and leaves a residual**. Four questions follow, and they can be asked of a type
system, a bounds check, a sanitizer, an interpreter, a solver or a guard page:

1. **Property.** Which *predicate* is established? Not "is it safe" but which
   one. "Every read is inside a live allocation" and "the result folds the bytes
   the request named" are different sentences, and \pat{p17} is a program where
   the first holds and the second fails.
2. **Bearer.** Who is obliged to establish it — the author in a comment, a
   compile-time check, a runtime compare-and-branch, a solver, an interpreter,
   the operating system, or nobody.
3. **Quantifier.** Over which **resource**, and which **executions**? Values? The
   trace? Allocations through *this* allocator? Machine-stack frames? Wall-clock
   time? This is the load-bearing coordinate and the one everyone omits.
4. **Residual.** What is left over, and who holds it now — including "nobody, and
   no instrument in the toolchain can see it."

*Residual* here is that fourth coordinate, and has nothing to do with a
regression residual, which is what the word means in \ref{sec:lies}.

On an easy bug all four are boring, which is why the abstraction stays invisible
most of the time. \pat{p02} copies a record into a fixed destination and the
attacker sets the length one byte too long. Property: the store is inside the
destination. Bearer: a runtime compare-and-branch. Quantifier: this store, every
execution. Residual: nothing — delete the test from the safe rung and it aborts
by name, while the same omission in C exits 0 with a plausible wrong number
(\ref{sec:hostile}). The interesting bugs make the third coordinate earn its
place.

\subsection{What this is: a taxonomy, with one prediction in it}
\label{sec:quadruple-predicts}

Say plainly what the rest of this section is. It is a **taxonomy of property
classes**, each with a worked instance from this corpus, graded against the
mechanisms that reach it and those that do not. The quadruple accounts, *after
the fact*, for every gap in \ref{sec:hostile}. That is weaker than "predictive",
and the record does not support the stronger claim.

The one row where a prediction was made and then confirmed is the free list.
\pat{p27} is a handle table over per-record `malloc`/`free`, and its proof
carries a temporal obligation rather than a spatial one — the record still exists
at the moment of the read — borne by a `PointsTo` permission that `deallocate`
consumes \src{patterns/p27-handle-table/verus.rs}. Read the quantifier off that
sentence: the guarantee ranges over **allocations released through this
allocator**. A structure that takes one slab and recycles slots out of a free
list never releases anything, so nothing consumes a permission and there is
nothing to inherit. The probe agreed: under `#![forbid(unsafe_code)]` a slot free
list admits use-after-recycle *and* a slot double-free yielding two aliased
handles, both silently wrong, with Miri reporting zero undefined behaviour — and a
generation tag does not rescue it, because the bump is a hand-written second
store, exactly the one C omits \src{.memory/01-ladder.md}.

**The prediction the project registered before that probe was a different one,
and it was wrong.** It generalised from a single refusal that a safe rung for any
pointer-backed structure is *either* an arena that never frees *or* the handle
table's runtime mechanism. Two reviewers found **four** outcomes independently,
and the third is the free list, where the type system is silent. The rule that
replaced it — *safe Rust's temporal guarantee is a guarantee about the allocator;
a structure that recycles its own storage gets no guarantee at all* — is derived
from four measured outcomes rather than from the abstraction, which was written
down eleven tasks after the probe \src{.memory/01-ladder.md}.

One confirmed prediction, one refuted one, and a taxonomy that earns its place by
accounting for the rest.

\begin{principle}{Name the resource the obligations quantify over}
Before claiming that a proof, a type system or a tool covers a bug class, write
down which **resource** its obligations range over. Then ask whether the bug
class lives in that resource — and, if it does not, whether a different encoding
would put it there.
\end{principle}

\begin{example}{Affine, not linear: a token you may simply drop}
A **linear** token must be spent — the program does not compile unless something
consumes it — while an **affine** token may be spent *or discarded*, and that one
word decides whether a proof about deallocation says *this release is legal* or
*this release happens*.

At this Verus pin the token is affine. \pat{p42}'s error path can drop it and the
file still verifies: `2 verified, 0 errors` on the leaking arm of the committed
control, while the positive control fails `error[E0382]: use of moved value`,
which is what says the tokens really are move-only and the probe is not vacuous
\src{patterns/p42-goto-cleanup/verus.rs}. The obvious repair is an encoding —
escrow the token in a ghost ledger and `ensures` its domain comes back empty on
every exit. That was built, it verified, it was published, and it was refuted: a
one-line ghost removal in place of the release satisfies the same `ensures` at
the same count while the program leaks, because that removal is the call the
release itself makes. Wrapping an affine resource in a map does not make it
linear; it makes the drop take one more line \src{.memory/04-verus.md}.

What survives is sharper than either published claim: **a token obligation is
only as strong as the smallest scope that can construct or discard the token.**
There is no linear, must-consume mode at this pin, so a repair has to come from
privacy — a Rust mechanism, not a Verus one.
\end{example}

\subsection{The taxonomy}
\label{sec:quadruple-table}

Rows are property classes; columns are mechanisms; every row carries an instance
from this corpus so the cell can be checked rather than believed.

| Property class · instance | Types (rustc) | Runtime | Sanitizer | Miri | MS proof | Full proof (Verus, this pin) |
|---|---|---|---|---|---|---|
| Spatial, outside the object · \pat{p02}, \pat{p09} `q >> 5` | no | **yes** | **yes** | **yes** | **yes** | yes |
| Spatial, in bounds and wrong · \pat{p09} `q >> 7`, \pat{p04} | no | no | **vacuous** | **vacuous** | **no** | yes |
| Temporal, through the allocator · \pat{p27} | **yes** | **yes** | **yes** | **yes** | **yes** | yes |
| Temporal, self-recycled storage · free-list probe ⁽¹⁾ | **no** | no | — | **no** | no | — |
| Resource occurrence — does the release happen · \pat{p42} | partly ⁽²⁾ | no | **yes** | **yes** | **no** | **no** ⁽³⁾ |
| A bounded resource the logic does not name — the machine stack ⁽⁴⁾ | no | yes, fail-stop | — | — | no | **no** |
| Termination · \pat{p22} | no | yes, watchdog ⁽⁵⁾ | no | no | no | **yes** ⁽⁶⁾ |
| Trace properties, information flow · \pat{p47} | no | no | **vacuous** | **vacuous** | no | **no** |
| A legal read of the wrong bytes · \pat{p17} | no | no | **vacuous** | **vacuous** | **no** | **yes** |
| Undefined behaviour touching no memory · \pat{p18} | no | only with debug assertions | UBSan yes, ASan no | yes, as a panic | yes ⁽⁷⁾ | yes |
| A rule vacuous in the target language · \pat{p38} | C no, Rust **vacuous** | no | TySan yes ⁽⁸⁾ | **vacuous** | **vacuous** | vacuous |
| Region aliasing, discharged before anything runs · \pat{p08} | **yes** | n/a | no ⁽⁹⁾ | **yes** | **no** | no |

Legend. `yes` — reaches this class, with a measurement behind it. `no` — silent,
and could in principle have seen it. `vacuous` — silent because there is no
violation of *this mechanism's own rule* to find, which is not the same as `no`;
see \ref{sec:quadruple-vacuous}. `—` — not measured. `MS proof` is Verus with the
functional postcondition stripped; `Full proof` keeps it.

**Columns.** Each column is one mechanism at one version, not a mechanism class.
*Types* is rustc's borrow checker and type system at this pin — a linear or
session-typed language reaches the free-list row that rustc does not. *Sanitizer*
is ASan, UBSan and TySan as this project builds them. *Full proof* is Verus at
this pin and no further: the trace row is what relational verification is built
for, and ct-verif, FaCT, Jasmin with EasyCrypt, Vale and the relational and
Cartesian Hoare logics behind them reach a class this column does not. Read every
`no` as *this mechanism, this version*, never as *nobody can*.

Three cells are results rather than gradings. **The in-bounds row's full-proof
verdict holds only while the specification does not inherit the author's
mistake**: move \pat{p09}'s `word_of` to `/128` so it matches the bugged shift and
Verus reports `20 verified, 0 errors` — a program proved to meet a specification
that *is* the bug \src{patterns/p09-bitset/NOTES.md}. **\pat{p08}'s MS-proof cell
sits inside the trusted body**, where a one-word substitution commits the
pattern's own undefined behaviour and only Miri notices (\ref{sec:proof}). And
**\pat{p42}'s cell is the retraction above.**

Notes. ⁽¹⁾ A reviewed probe, not a shipped pattern. ⁽²⁾ `Drop` discharges it for
the ordinary spelling, and leaking is *safe* in Rust, so \pat{p42} excludes
`ManuallyDrop`, `mem::forget`, `Box::leak` and `Box::into_raw` by declaration.
⁽³⁾ Two encodings measured, both admitting a verifying leaker; a third is open
\src{.memory/04-verus.md}. ⁽⁴⁾ ⚠ Provisional and unreviewed \src{RECAP.md}.
⁽⁵⁾ A timeout is a runtime mechanism that reaches non-termination, and this
corpus's own classifier is one: the gate re-runs each of \pat{p22}'s 8 hung cells
at ten times the budget, failing if any terminates. ⁽⁶⁾ Verus demands a
`decreases` on every exec loop by default, so the bearer is the prover's
discipline and not the author's intent — and termination is *one* liveness
property, with `decreases` reaching neither fairness nor eventual response.
⁽⁷⁾ Raised as `possible bit shift underflow/overflow` on the expression itself,
so the bearer is default arithmetic checking, not the memory-safety argument.
⁽⁸⁾ ASan fires only under `-fstrict-aliasing`, a flag and not an optimisation
level, and UBSan has no strict-aliasing check at all
\src{patterns/p38-alias-pun/NOTES.md}. ⁽⁹⁾ Silent because fortification rewrote
the call to `__memcpy_chk` and the check lives in the interceptor
(\ref{sec:hostile}).

\subsection{Vacuous is not blind}
\label{sec:quadruple-vacuous}

A coverage table cannot tell the difference between a mechanism silent because it
cannot see and one silent because there is nothing there to see. Both print an
empty cell, and distinguishing them is most of the work.

\pat{p38} is the worked case. Strict aliasing is a rule of the C abstract
machine; Rust has no type-based aliasing rule at any rung, and `&mut`'s `noalias`
is uniqueness rather than type identity. There is no obligation for a Rust
mechanism to discharge — every obligation in that pattern's proof is spatial, and
what excludes the harm is a property of the language, assumed rather than proved,
by every rung including the naive safe one \src{patterns/p38-alias-pun/verus.rs}.
The evidence that this is vacuity and not blindness is a control: Miri is silent
on `r4_pun`, which performs the exact analogue of the C violation, because in
Rust it is not a violation \src{patterns/p38-alias-pun/NOTES.md}.

The same test grades the sanitizer and Miri cells on the in-bounds rows. A read
inside its own allocation breaks no rule ASan or Miri enforces, so the silence is
not a miss — and \pat{p17} makes that checkable, because the pattern's model
declares the disclosing input *clean*, so a sanitizer report there would have
failed the gate \src{patterns/p17-http-range/NOTES.md}.

Two silences, then — and a third worth separating. \pat{p09}'s in-bounds index bug
is invisible because the *specification* was silent, and could have been
strengthened. \pat{p47}'s leak is invisible because the *logic* is silent, and
cannot be. The tree records \num{totals.miri_runs} Miri runs with
\num{totals.miri_ub} undefined-behaviour findings, which says the shipped rungs
are clean and nothing about which silence a given empty cell is.

\begin{example}{Three failures stacked: constant-time comparison}
\pat{p47}'s proof rung fails on three independent grounds at once. Take the
verified kernel, replace the or-accumulating tag loop with an early-exiting one
plus a lemma saying the accumulator is sticky, and Verus reports `14 verified, 0
errors` with the kernel's own obligation count unchanged at 3. The binary then
leaks `+7088` `Ir` per call between two inputs that print the same checksum.

First, the `ensures` denotes the **value** returned, and the defect does not
change it — the two kernels are extensionally equal, and the added lemma is the
proof of that. Second, a timing property is about the **trace**, and this
assertion language has no term denoting a trace, no cost model, and no way to
quantify over the two executions a non-interference property compares: not hard
here, but not expressible *at this pin*, which is the row relational verification
exists to reach. Third, the property is not one of this program at all but of the
machine code, which LLVM chooses after Verus has finished — the constant-time
compilation problem, a decade old and the stated motivation for CompCert-CT,
Jasmin and FaCT. This corpus contributes an instance, not the observation.
\src{patterns/p47-ct-compare/verus.rs}
\end{example}

That third failure does not need a fifth coordinate. Quantifier has two halves —
the resource, and the *artefact* — and "which artefact does this range over?" is
the same kind of question as "which resource?". This project discharges it by
measurement rather than by a new coordinate: the gate requires the proved rung's
machine code to be byte-identical to the unproved one's, `exact` on
\num{totals.identity_exact} of \num{totals.patterns} patterns.

\begin{takeaway}
Before accepting any safety claim — a language's, a tool's, a proof's — write down
four things: the predicate, its bearer, what it quantifies over, and what is
left. The third is missing from the marketing, and it is what lets you state the
fourth. "Memory-safe" is not a property; it is a family of properties over
different resources, and a mechanism covers exactly the members whose resource it
names.
\end{takeaway}
