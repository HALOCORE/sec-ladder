%% ver_A section 9 -- NAVIGATION, not argument. Every principle is stated and
%% motivated in the section that holds its evidence; this page is the checklist.
%% ⚠ NEVER cite a principle by ordinal anywhere in this paper -- an ordinal
%% breaks the moment a principle moves. Point with \ref, and name the case.
%% ⚠ STATE NO COUNT HERE. The list is the count; a written number ("Nine") goes
%% stale the moment a principle lands, moves or merges, and one did.
%% ⚠ Keep this list in sync -- grep the principle environment across sections/
%% and list them in reading order. Do NOT write that environment's opening tag
%% in a comment: build_data.py counts principles by regex over the raw body and
%% a mention here inflates the count. The \ref targets are section labels, so
%% the list survives a principle being re-worded or re-homed in its section.

\section{Principles, gathered}
\label{sec:principles}

These rules follow from \ref{sec:quadruple} and the measurements under it. Each
is stated where its evidence is, because a rule separated from the failure that
produced it is only advice; this page is the checklist, with a pointer to the
section that argues it and to the case that earns it. Where the failure is one
this project committed, that section says so — nineteen published claims were
retracted on the way here, and \ref{sec:lies} collects the sharpest
\src{results/SYNTHESIS.md}.

1. **Never ship the naive rung as safe Rust.** A benchmark that reports the
   mechanical index-by-index port as *"safe Rust"* is measuring whether anyone
   tuned the code. \ref{sec:ladder} — *a lost memcpy idiom, not a check*.
2. **The precondition is structural; the attack is data.** A `requires` may state
   only structural facts; every attacker-controlled quantity is an argument, and
   the security property goes in the `ensures`. \ref{sec:method} — *a
   precondition that assumes the attack away*.
3. **A silent detector and an absent detector are one observation.** Never record
   "the tool found nothing" until that tool, in that build, on that box, has been
   shown reporting something. \ref{sec:hostile} — *three detectors, three
   measured blind spots*.
4. **Publish the pair, and name the side you did not search.** A safety cost is a
   property of two programs, not of a language: ship the number, the pair of
   spellings it is a difference of, and which side was searched. \ref{sec:cost} —
   *510× on one pattern's tax*.
5. **Can the optimiser see the bound?** A bounds check costs what the optimiser
   cannot delete, so ask where the bound comes from rather than how many checks
   there are. \ref{sec:cost} — *the fact the middle-end already had*.
6. **A proof pays only where it licenses something.** Verification is not an
   optimisation: it removes no check the compiler was going to emit, it
   authorises code that never had one. \ref{sec:proof} — *a proved safe rung, and
   slower for it*.
7. **The obligation count is not a coverage measure.** Report which properties
   are stated and pin the contract textually, because the count is invariant
   under exactly the weakenings that matter. \ref{sec:proof} — *a ledger that
   verifies while it leaks*.
8. **A trusted precondition is an axiom about the world.** Weakening one is
   silent and non-local, a small number is not by itself a small trusted base,
   and what you counted is not the trusted computing base. \ref{sec:proof} — *the
   escape hatch the verifier prints for you*.
9. **Name the resource the obligations quantify over.** Before believing that a
   proof, a type system or a tool covers a bug class, write down which resource
   its obligations range over — then ask whether a different encoding would put
   the class there. \ref{sec:quadruple} — *a permission you may drop*.

The last is the result. The others are ways of noticing that an obligation moved
and that nobody wrote down where it landed.
