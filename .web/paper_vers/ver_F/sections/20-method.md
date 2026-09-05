%% Methodology.  Definitions first, then the dataset, then what is measured,
%% then the rules that shape the numbers.
%%
%% ⚠ The composition table is FROZEN.  It is what
%% `harness/tools/composition.py` prints today and the script drift-checks it
%% against patterns/*/spec.md; re-run it before touching a count.  The total is
%% live, so a landed pattern makes the rows visibly not sum.
%% ⚠ Admission history (fact-check A8, gaps review): six earlier temporal
%% refusals rested on Rust-side reasons (CLAUDE.md rule 6, RECAP finding 53);
%% the bar was replaced by the C-side-only one and the candidates re-admitted
%% (SYNTHESIS §0).  Several rows of Finding 8 exist because of that.
%% ⚠ Catalogue: 47 rows pre-project, grown to 49 (SYNTHESIS §5, §7) — A7.
%% ⚠ Toolchain versions are from data/index.json `toolchain` and TOOLCHAIN.md.
%% ⚠ Builds per program: 8 targets (4 C = 2 versions x 2 compilers, 4 Rust)
%% x 2 opt levels x 2 inlining settings = 32; p01 ships 28, hence "up to".
%% ⚠ Rule 1 as enforced: same instruction stream; byte-identical on all but
%% five, where the differences are link addresses and, on one, an uncalled
%% 26-byte stub (SYNTHESIS §4, CLAIMS 1.19) — M9.
%% ⚠ "repeatable for a fixed environment", not "reproducible across sessions":
%% SYNTHESIS §6 trap 7(a).
%% ⚠ Contracts bound length not contents: a 26-of-26 result not re-derived at 33
%% (SYNTHESIS §7) — R4.
%% ⚠ "verified items", never "obligations" (CLAIMS 3.7) — M8.
%% ⚠ Vocabulary: "comparable", not "licensed"; "checking script", not "gate".
%% ⚠ CLAIMS.md 3.1: "plain, unchecked C", never "idiomatic C".
%% ⚠ CLAIMS.md 3.8: "cheapest found", never "minimum".
\section{Methodology}
\label{sec:method}

\subsection{Six versions of one program}

Each program is one small function — a record walker, a bounded stack, a binary search, a reference-counted stack — chosen because it carries a bug from a real class, and written six ways. The six versions must agree on every well-formed input and differ only in what enforces memory safety.

| version | what it is | what enforces safety |
|---|---|---|
| plain C | the program as a careless author ships it: the check is missing | nothing |
| hardened C | the same C with the missing check written in | the author, by hand |
| safe Rust, port | a line-for-line translation of the C | the compiler's bounds check on every access |
| safe Rust, tuned | the same program rewritten so the compiler can remove checks it can prove unnecessary | the compiler's bounds check, where it survives |
| unsafe Rust | raw pointers and unchecked access, the checks switched off | nothing at run time |
| verified Rust | the unsafe version plus a Verus specification and proof | the prover, at compile time |

\figure{ladder}{The six versions. C starts fast and unchecked and gains safety by adding a check; Rust starts checked and loses cost by tuning or by opting out. The verified version runs the unsafe code with its obligations discharged.}

The plain C is not "idiomatic C". A copy with the capacity in scope and no test against it is a defect, and it is the defect these programs exist to price. The hardened C is what separates "C is faster" from "C skipped the check": without it every plain-C figure flatters Rust, so wherever this paper compares C with Rust the hardened row is present.

\subsection{The programs}

We started from a catalogue of 47 candidate bug classes written before any measuring began, grown to \num{totals.catalogue} during the project, and built \num{totals.passing.patterns}. The admission rule is about the C alone: a candidate has to compute the right answer on benign input, exhibit its bug on an adversarial input, and use a C mechanism no built program already used; it is refused for duplicating a built mechanism, not because the Rust or the proof looks hard. The project did not always apply that rule: an audit found six earlier refusals resting on Rust-side reasons — among them that the safe version reproduced the C bug exactly — and those candidates were re-admitted under the C-side rule. Several rows of Finding 8's table are there because of that change. Classified by the safety line each C program omits:

| bug class | programs | examples |
|---|---:|---|
| spatial — an index or length that can leave its buffer | 15 | buffer copy, record walker, binary search, bitset, NUL scan |
| temporal — use of storage after it was released or recycled | 6 | handle table, intrusive lists, tree delete, free-list pool, reference counting |
| logical — an in-bounds check on the wrong thing | 3 | ring buffer, rotate, protocol state machine |
| type confusion | 2 | tagged union, aliasing pun |
| aliasing | 2 | overlapping copy, interned pool |
| one each: resource leak, timing side channel, undefined shift, non-termination, and a calibration program with no bug | 5 | `goto` cleanup, constant-time compare, varint decoder, hash probe, array sum |

Every program appears, with its measured costs, in the table under Finding 1.

\subsection{What we measure}

**Cost.** The unit is instructions executed per call of the measured function, counted by valgrind's callgrind \cite{valgrind07} inside that function's symbol only. For a fixed environment it is repeatable to the instruction, which wall clock on a shared machine is not. Every cost figure is at `-O3`, with the measured function kept out of line so that it has a symbol to attribute work to, on two inputs per program — `small` and `large` — unless it says otherwise.

**Correctness.** Each program has an independent reference implementation in Python. A checking script rebuilds every version, runs every build on every input, and compares its output and exit status with the reference. The inputs include benign ones and hostile ones written by hand to trigger that program's bug; \num{totals.adversarial_zero_call} of the \num{totals.adversarial_inputs} hostile inputs are rejected by the shared driver before the measured function runs, so on those every version agrees trivially.

**Detectors.** The plain and hardened C are additionally run under AddressSanitizer and UBSan \cite{asan12}, in one build configuration; the unsafe Rust — and only the unsafe Rust — under Miri \cite{stackedborrows20}, an interpreter that executes Rust hunting for undefined behaviour; the verified version through Verus \cite{verus23}, which discharges its proof obligations with the Z3 solver \cite{z3}. Two of the \num{totals.passing.miri_runs} Miri runs hit their three-minute budget and were never completed.

**Toolchain and scale.** gcc 13.3.0; clang 22.1.6; rustc 1.97.1, whose LLVM is the same 22.1.6; Verus 0.2026.08.09 with its pinned standard library; valgrind 3.27.1; glibc 2.39; one Xeon Gold 6230 host. Each version is built at two optimisation levels and in two inlining settings, and the C versions by both compilers, so a program has up to 32 builds: \num{totals.passing.cells} in all, \num{totals.passing.adversarial_runs} hostile runs, and \num{totals.passing.verus_verified} verified items — Verus counts functions, loop bodies and sub-proofs, not individual conditions — with \num{totals.passing.verus_errors} errors. The measurement records, every program's six sources, and the scripts that re-derive each corpus figure in this paper accompany the report, and the figures are recomputed from those records when this document is built.

\subsection{Three rules that shape every number}

**The proof may not change the code.** A program's numbers do not count unless its verified version and its unsafe version compile to the same instruction stream at `-O3` — byte-identical on all but five programs, where the differences are addresses the linker chose and, on one, a 26-byte function the proof leaves in a table of function pointers and nothing ever calls. Without that rule we would be pricing the proof's effect on the compiler rather than the cost of the code. Its consequence is that the proof's run-time cost is zero by construction; Section \ref{sec:proof} says what the rule buys and what it cost us.

**Each version's allowed ways of writing it are fixed in advance.** Each program declares, before it is measured, which idioms each version may use, because a cheaper way of writing one version was found, more than once, after a comparison had been published. Every superlative in this paper therefore reads *cheapest found*, never *minimum*: a search that stopped is not a proof that nothing cheaper exists.

**A difference is only reported where the two versions are comparable.** The instruction count covers the measured function alone. Two versions may be subtracted only when they call the same things outside that function; otherwise the difference is between two different programs, and we do not print it. \num{totals.buckets.licensed} of the \num{totals.passing.patterns} tuned-safe-versus-unsafe differences are comparable, and every cross-program statistic in Section \ref{sec:cost} is over those. The ten that are not include six of the seven programs built last, most of them temporal, so the cost statistics speak mostly for the bounds-check programs.
