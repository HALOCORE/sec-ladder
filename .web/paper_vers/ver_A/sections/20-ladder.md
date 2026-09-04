%% ver_A -- the ladder.
%% Sources, ranked: .memory/01-ladder.md, .memory/04-verus.md (p11's refusal --
%% r4_cstr DOES escape, at four axioms; "cannot reach it at all" is superseded
%% and must not be repeated), results/synthesis.md, p02-buffer-copy.json.
%% ⚠ "What you still trust" is the residual, and it was FALSE in an earlier
%% draft: R2/R3 read "nothing", R1 and R1h shared "everything".  Do not shorten
%% this column back to one word.  ⚠ "Idiomatic C" is not a name for R1 -- that
%% is the same program with the check missing, a defect and not an idiom.
%% ⚠ ONE HOME here: p11's refused CStr rung.  R2-vs-R3's distribution (median
%% 7.26x) lives in sec:cost -- rung defined here, number quoted there, once.

\section{The ladder}
\label{sec:ladder}

Every pattern is one small C kernel — a TLV walker, a bounded stack, a `strncpy`
truncation — implemented six times. The rungs must be **semantically equivalent on
well-formed input**, checked by the gate against an independent reference
implementation on every committed blob, and must differ only in *what enforces
memory safety*.

| rung | what it is | where the check lives | what you still trust |
|---|---|---|---|
| **R1** C | plain C99 with no bounds checks, *including* the bug class the pattern models | absent — the program trusts the wire | everything, starting with the wire |
| **R1h** hardened C | the same kernel plus the bounds check a careful C programmer writes; same signature, same driver | hand-written, and only where you remembered to write it | the compiler, libc, and that you wrote the check everywhere |
| **R2** safe Rust, naive | the mechanical port: `for i in 0..n { … v[i] … }`, indexing, `Vec`, no cleverness. Zero `unsafe` | the language, at every access | the compiler, its standard library's own `unsafe`, and the absence of a soundness bug |
| **R3** safe Rust, tuned | the same semantics respelled so LLVM can hoist: reslice once then iterate, `copy_from_slice`, `chunks_exact`. Still zero `unsafe` | the language still — but spelled so the check leaves the loop | as R2 |
| **R4** unsafe Rust | `get_unchecked`, raw pointers, `copy_nonoverlapping`. Asserted correct by its author, neither checked nor proved | removed; the obligation moves to the programmer | everything R3 trusts, plus every `unsafe` block |
| **R5** unsafe Rust + Verus | R4's executable code plus proofs discharging every unsafe precondition. `requires`, `ensures`, `invariant`, `decreases` are ghost and erase | discharged before run time by a solver, not at run time by the CPU | the `external_body` wrappers — counted, per pattern — plus Z3, Verus's encoding of Rust into SMT, rustc's ghost erasure, and LLVM |

Every pattern that models a bug ships R1h; the one calibration pattern has no bug
to harden against. Corpus-wide the last row costs \num{totals.tcb_items} trusted
items over \num{totals.tcb_lines} trusted lines, against
\num{totals.verus_verified} items verified and \num{totals.verus_errors} errors.

One control settles why R5 sits on top of R4 rather than on top of R3: prove the
*safe* rung panic-free and nothing in the binary changes, because rustc never
learns what the solver knew. A proof pays only where it **licenses unsafe code**,
which is exactly what R5 is (\ref{sec:proof}).

\subsection{Two climbs, not one ladder}

The rungs are not one sequence. They are two tracks approaching the same place
from opposite ends. **C starts fast and unchecked and has the check added by
hand**; **Rust starts checked by the language and has the cost taken back out.**
They meet in the middle, at R1h against R4 — the one comparison in the corpus with
no backend difference in it, because the clang this project builds C with is
bit-for-bit the LLVM its rustc ships. Any gap there is the *language*.

Read as a sequence of *bearers*, the two tracks are one thing, and it is not a
sequence of safety levels. Every rung takes an obligation that was somewhere and
puts it somewhere else: R1 leaves it on the wire, R1h hands it to the
programmer's discipline, R2 and R3 to the language, R4 back to the programmer as
a written promise, R5 that promise to a solver. **Not one of those moves makes
the obligation go away.** The table's last column is what each move leaves
behind, which is why it is never empty and why it is the hardest column in this
paper to fill in honestly. \ref{sec:quadruple} names it — the *residual*, the
fourth coordinate of a guarantee.

\begin{example}{One kernel, six rungs — `p02`, a buffer copy}
A `u16` length prefix off the wire says how many bytes to copy into a
fixed-capacity destination; the kernel returns a checksum of what it copied. The
source length and the destination capacity are both parameters. **R1 has them and
trusts the wire instead** — CWE-787 as it is actually written, which is what makes
the comparison honest.

Executed instructions per kernel call, `-O3 isolated`, kernel-exclusive, on the
two shipped inputs (61 and 4092 bytes copied per call):

| rung | cell | small | large |
|---|---|---:|---:|
| R1 | `c-gcc` / `c-clang` | 202 / 193 | 8 765 / 9 764 |
| R1h | `c-gcc-h` / `c-clang-h` | 207 / 205 | 8 770 / 9 776 |
| R2 | `safe_naive` | 392 | 11 211 |
| R3 | `safe_tuned` | 212 | 9 783 |
| R4 | `unsafe` | 201 | 9 772 |
| R5 | `verus` | 201 | 9 772 |

Four things to take from one row of numbers. **The hand-written C check costs +5
(gcc) and +12 (clang), identically at both sizes.** **Tuned safe Rust costs +11
against unsafe Rust, also identically at both sizes** — flat, not proportional.
**R5 equals R4 exactly**, because the two kernels are byte-identical machine code,
so the zero is entailed rather than observed. And **R2's apparent +191 is not a
safety tax**: the record marks that row not licensed for differencing, since only
the unsafe rung calls `memcpy`. It was rustc failing to idiom-recognise one
spelling of a byte-copy loop — published as an `O(n)` bounds-check tax, and
retracted. Under hostile input the six separate completely, and deleting the
bound test from the safe rung *panics* where C exits 0 (\ref{sec:hostile}).
\src{results/synthesis.md}
\end{example}

\subsection{R4 is not "R5 without the proof"}

This is the constraint a reader must not miss, and it inverts the intuition. The
gate pins the unsafe rung and the verified rung to the **same machine code** —
`identity: unsafe ≡ verus` at `-O3`, byte-exact on \num{totals.identity_exact} of
\num{totals.patterns} patterns and equal up to pc-relative displacements on the
remaining one. That pin is what licenses *"a proof costs zero instructions"*, and
it has a second consequence: **an R4 here is not a program merely permitted to
use `unsafe` — it is a program that must have a byte-identical twin the prover
accepts.** R4 is bounded by what the pinned Verus and its standard library can
express. R3 is bounded by nothing.

\begin{retraction}{The cheapest unsafe rung is cheaper by construction}
Published as a fact available *without measuring* — every safe program is
textually an admissible unsafe rung, so the inclusion is free. It is a reason, not
a result, it is false here, and the counterexample is the project's own gate: once
every pattern pins R4 ≡ R5, the admissible unsafe class is constrained by the
prover and the admissible safe class is not. The two classes are **incomparable,
not nested**, and the inclusion runs the opposite way from the one that was
published. \src{.memory/01-ladder.md}
\end{retraction}

Two measured consequences, running in opposite directions. **On `p16` the safe
class reaches a spelling the unsafe class cannot afford**: the `chunks_exact(32)`
fold over the TLV walker's records is admissible as safe Rust at **zero** trusted
items and as an unsafe rung needs **five**, on a pattern whose entire
memory-safety claim is *one* trusted `requires`.

**On `p11` the cheaper unsafe spelling is the one that is refused.** A NUL scan
respelled through `CStr` measures **−17 526 instructions per call on the large
input** — about 35% of that cell, in the whole-program marginal convention `p11`
publishes in — and is not shipped. But note what the refusal is: the four rejected
items *can* be escaped, first try, at `2 verified, 0 errors`, by writing four
hand-written axioms no gate stage checks. So the honest sentence is not *"the
prover cannot reach it"* — it is that the unsafe class reaches it **only by moving
the obligation into the trusted base**, while the safe class reaches
`core::slice::memchr` at zero. The bearer moved, and the price moved with it into
a different unit. (The candidate is +3 448 *dearer* on the small input, so it is
not uniformly cheaper.) \src{.memory/04-verus.md}

So **each safe-versus-unsafe difference here is measured against an unsafe rung
held above its true floor**, and reads more favourably to safe Rust than the
pattern warrants — which is not a claim that safe Rust is cheaper, but a
statement that the comparison is not a language fact in either direction.

\begin{principle}{Never ship the naive rung as safe Rust}
R2 and R3 are the same language with the same guarantee; only the spelling
differs. A benchmark that reports the mechanical `for i in 0..n { … v[i] … }`
port as *"safe Rust"* is not measuring safety, it is measuring whether anyone
tuned the code — the commonest way to overstate the tax, and an overstatement
\ref{sec:cost} measures rather than asserts. `p02` is why: its naive rung's whole
apparent penalty was a lost `memcpy` idiom, and none of it a bounds check.
\end{principle}

Everything that follows prices one of these moves, or the refusal to make one:
\ref{sec:hostile} is what it costs to leave the obligation on the wire,
\ref{sec:cost} what it costs to hand it to the language, and \ref{sec:proof} what
it costs — and what it fails to buy — to hand it to a solver.
